# AI Bug Pattern Catalog

> **What this is:** A catalog of real bug patterns we've observed AI code generators
> producing repeatedly. These are NOT hypothetical — each pattern is documented from
> production incidents, code reviews, and research studies.
>
> **How to use this:** Before analyzing any code, read through this catalog to calibrate
> your detection instincts. Then cross-reference each pattern against the code you're
> auditing.

## Table of Contents

1. [Transaction & Atomicity Bugs](#1-transaction--atomicity-bugs)
2. [Edge Case Blindness](#2-edge-case-blindness)
3. [Security Oversights](#3-security-oversights)
4. [Performance Landmines](#4-performance-landmines)
5. [Business Logic Errors](#5-business-logic-errors)
6. [Error Handling Gaps](#6-error-handling-gaps)
7. [Concurrency & Race Conditions](#7-concurrency--race-conditions)
8. [Data Integrity Issues](#8-data-integrity-issues)
9. [Configuration & Environment Assumptions](#9-configuration--environment-assumptions)
10. [Testing Blind Spots](#10-testing-blind-spots)

---

## 1. Transaction & Atomicity Bugs

### Pattern 1.1: Missing Transaction Boundaries
**Frequency:** VERY HIGH | **Severity:** CRITICAL

```python
# ❌ AI-GENERATED: Each operation commits independently
async def process_payment(order):
    payment = await create_payment(order)
    await save_to_database(payment)
    await send_confirmation_email(order.email)
    return payment
```
**What goes wrong:** Network hiccup after `create_payment` but before `save_to_database`
→ duplicate charges. This cost one team $12,400 in refunds.

**What to look for:** Multiple async/database operations without an explicit transaction
wrapper. Especially dangerous in payment, order, and user registration flows.

### Pattern 1.2: Partial Rollback
**Frequency:** HIGH | **Severity:** CRITICAL

```javascript
// ❌ AI-GENERATED: Only rolls back one of three operations
async function transferFunds(from, to, amount) {
  const tx = await db.beginTransaction();
  try {
    await debit(tx, from, amount);  // This gets rolled back ✓
    await credit(to, amount);       // This does NOT ✗
  } catch (e) {
    await tx.rollback();  // Only rolls back operations on 'tx' connection
    throw e;
  }
}
```
**What to look for:** Some operations use the transaction object, others don't. Check
that ALL state-changing operations within a try block share the same transaction.

### Pattern 1.3: No Idempotency for Payment Operations
**Frequency:** MEDIUM | **Severity:** CRITICAL

```python
# ❌ AI-GENERATED: No idempotency key, no duplicate check
@app.post("/charge")
async def charge(request: ChargeRequest):
    payment = await payment_gateway.charge(request.amount, request.card_token)
    return {"status": "success", "payment_id": payment.id}
```
**What to look for:** Payment/charge endpoints without idempotency keys, duplicate
checks, or retry-safe logic. A network retry can cause double charges.

---

## 2. Edge Case Blindness

### Pattern 2.1: Empty/Null Input Assumption
**Frequency:** VERY HIGH | **Severity:** HIGH

```typescript
// ❌ AI-GENERATED: Assumes array is non-empty
function getLatestOrder(orders: Order[]): Order {
  return orders.sort((a, b) => b.date - a.date)[0];
  // TypeError: Cannot read property '0' of undefined (empty array)
  // Also: mutates input array (sort is in-place)!
}
```
**What to look for:** Array access without length checks. String methods without
null/empty guards. Object property access without null checks.

### Pattern 2.2: Boundary Value Blindness
**Frequency:** HIGH | **Severity:** HIGH

```python
# ❌ AI-GENERATED: Off-by-one in discount logic
def calculate_discount(price, percentage):
    return price - (price * percentage / 100)
    # What if price is 0? What if percentage is 0? What if percentage > 100?
    # What about negative values? What about floating point precision?
```
**What to look for:** Math operations without range validation. Comparison operators
(`<` vs `<=`) at boundaries. Integer overflow possibilities. Floating point precision
in financial calculations.

### Pattern 2.3: Missing Date/Time Edge Cases
**Frequency:** MEDIUM | **Severity:** MEDIUM

```javascript
// ❌ AI-GENERATED: Ignores timezone, DST, leap years
function getAge(birthdate) {
    const today = new Date();
    return today.getFullYear() - birthdate.getFullYear();
    // Wrong for someone whose birthday hasn't happened yet this year
    // Also: timezone differences can shift the date
}
```
**What to look for:** Date math without timezone handling. Assumptions about system
clock. Missing DST transition handling. Duration calculations using approximate values.

---

## 3. Security Oversights

### Pattern 3.1: SQL Injection via String Interpolation
**Frequency:** HIGH | **Severity:** CRITICAL

```javascript
// ❌ AI-GENERATED: Classic SQL injection
app.post('/login', (req, res) => {
  const query = `SELECT * FROM users WHERE email = '${req.body.email}'`;
  db.query(query, (err, user) => { /* ... */ });
});
// Input: admin@company.com' OR '1'='1' -- 
// Result: logs in as admin without password
```
**What to look for:** String interpolation/template literals in SQL queries. Direct
concatenation of user input into queries. Missing parameterized queries.

### Pattern 3.2: Missing Authorization Checks
**Frequency:** HIGH | **Severity:** CRITICAL

```python
# ❌ AI-GENERATED: Authenticates but doesn't authorize
@app.get("/api/users/{user_id}/documents")
@require_auth  # Checks "are you logged in?" ✓
async def get_documents(user_id: int, current_user: User = Depends(get_current_user)):
    return await document_service.get_for_user(user_id)
    # Does NOT check "are you allowed to see THIS user's documents?" ✗
```
**What to look for:** Endpoints that check authentication but not authorization.
User A can access User B's resources by changing an ID parameter.

### Pattern 3.3: Secrets in Code
**Frequency:** MEDIUM | **Severity:** CRITICAL

```python
# ❌ AI-GENERATED: Hardcoded credentials (often in "example" code)
API_KEY = "sk-abc123def456"  # Copy-pasted from docs
DATABASE_URL = "postgresql://admin:password123@localhost/db"
```
**What to look for:** Hardcoded API keys, passwords, tokens, connection strings.
"Temporary" credentials that will ship to production.

### Pattern 3.4: Insecure Default Configurations
**Frequency:** MEDIUM | **Severity:** HIGH

```yaml
# ❌ AI-GENERATED: Debug mode on, CORS wide open
DEBUG: true
CORS_ORIGINS: ["*"]
JWT_EXPIRY: 365d
RATE_LIMIT: none
```
**What to look for:** Debug mode enabled, permissive CORS, long token expirations,
disabled security features in configuration files.

---

## 4. Performance Landmines

### Pattern 4.1: N+1 Query Pattern
**Frequency:** VERY HIGH | **Severity:** CRITICAL

```javascript
// ❌ AI-GENERATED: N+1 query — each post triggers separate queries
async function getUserPosts(userId) {
  const posts = await Post.findAll({ where: { userId } });
  for (let post of posts) {           // 1 query for posts
    post.author = await User.findById(post.userId);      // N queries!
    post.comments = await Comment.findAll({ where: { postId: post.id } }); // N queries!
  }
  return posts;
  // 5 test posts: 11 queries (fast)
  // 500 real posts: 1001 queries (database at 100% CPU)
}
```
**What to look for:** Database queries inside loops. Missing eager loading, joins, or
batch queries. Check every `.findById()` or `.findAll()` inside `for`/`.map()`/`.forEach()`.

### Pattern 4.2: O(n²) in Production Paths
**Frequency:** HIGH | **Severity:** HIGH

```python
# ❌ AI-GENERATED: Nested loops — fine for 10 items, deadly for 10,000
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):          # O(n)
        for j in range(i + 1, len(items)):  # O(n) nested = O(n²)
            if items[i].id == items[j].id:
                duplicates.append(items[i])
    return duplicates
```
**What to look for:** Nested loops over collections. `.filter()` inside `.map()`.
Sorting unnecessarily. Unindexed lookups in hot paths.

### Pattern 4.3: Unbounded Memory Growth
**Frequency:** MEDIUM | **Severity:** HIGH

```python
# ❌ AI-GENERATED: Loads everything into memory
async def export_all_users():
    users = await User.find_all()  # Loads 1 million users into RAM
    csv_data = generate_csv(users)
    return csv_data  # OOM on large datasets
```
**What to look for:** Loading entire tables into memory. Appending to arrays without
bounds. Missing pagination on list endpoints. Streaming alternatives not used.

### Pattern 4.4: Missing Database Indices
**Frequency:** MEDIUM | **Severity:** HIGH

```sql
-- ❌ AI-GENERATED: No index on frequently queried column
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(50),
    created_at TIMESTAMP
);
-- Query: SELECT * FROM orders WHERE user_id = ? AND status = 'pending'
-- Without index on (user_id, status): full table scan every time
```
**What to look for:** New tables or columns without indices that match query patterns.
Check JOIN conditions, WHERE clauses, and ORDER BY fields.

---

## 5. Business Logic Errors

### Pattern 5.1: Double Application of Discounts
**Frequency:** MEDIUM | **Severity:** HIGH

```python
# ❌ AI-GENERATED: No check if discount already applied
def apply_discount(order, discount_code):
    discount = DiscountCode.find_by_code(discount_code)
    order.total -= discount.amount
    order.save()
    # What if another discount was already applied?
    # What if this is a loyalty discount stacking on a promo code?
```
**What to look for:** Mutations that don't check current state before applying changes.
Discount stacking, duplicate processing, cumulative modifications without guards.

### Pattern 5.2: Incorrect Currency/Precision Handling
**Frequency:** MEDIUM | **Severity:** CRITICAL

```javascript
// ❌ AI-GENERATED: Float arithmetic for money
const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
// 0.1 + 0.2 = 0.30000000000000004 in floating point
// Over thousands of transactions, cents accumulate into dollars
```
**What to look for:** Float/double for monetary values. Missing rounding to correct
decimal places. Currency conversion without precision handling.

### Pattern 5.3: Stale Data Decisions
**Frequency:** MEDIUM | **Severity:** HIGH

```python
# ❌ AI-GENERATED: Reads inventory, then writes — race condition window
def place_order(product_id, quantity):
    product = Product.get(product_id)       # Read: stock = 5
    if product.stock >= quantity:            # Check: 5 >= 5 ✓
        order = Order.create(product_id, quantity)
        product.stock -= quantity            # Write: stock = 0
        product.save()
        # Another request could read stock=5 between our read and write
```
**What to look for:** Read-check-write patterns without locking. Optimistic concurrency
without version checks. `SELECT ... FOR UPDATE` not used where needed.

---

## 6. Error Handling Gaps

### Pattern 6.1: Silent Failures
**Frequency:** VERY HIGH | **Severity:** HIGH

```python
# ❌ AI-GENERATED: Catches and silently swallows errors
try:
    result = external_service.call(data)
except Exception:
    pass  # Error swallowed — caller has no idea it failed
    # Also: catching bare Exception includes KeyboardInterrupt, SystemExit
```
**What to look for:** `except:` or `except Exception:` with `pass`. Missing logging in
catch blocks. Catching too broad an exception class.

### Pattern 6.2: Missing Retry Logic
**Frequency:** HIGH | **Severity:** HIGH

```python
# ❌ AI-GENERATED: Fails immediately on transient errors
async def fetch_user_data(user_id):
    response = await http_client.get(f"/api/users/{user_id}")
    return response.json()
    # Network blip, DNS hiccup, load balancer timeout — all crash immediately
```
**What to look for:** External API calls without retry. Database queries without retry.
No exponential backoff. Missing timeout configuration.

### Pattern 6.3: Incomplete Error States
**Frequency:** MEDIUM | **Severity:** MEDIUM

```typescript
// ❌ AI-GENERATED: Only handles success and "generic error"
type AsyncState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
  // Missing: empty state, partial success, rate limited, validation errors
};
```
**What to look for:** Binary success/failure models that don't represent real-world
complexity. Missing states like: loading, empty, rate-limited, partial-success,
validation-error, timeout.

### Pattern 6.4: Resource Leaks in Error Paths
**Frequency:** MEDIUM | **Severity:** HIGH

```python
# ❌ AI-GENERATED: File handle leaks on exception
def process_file(path):
    f = open(path, 'r')
    data = parse(f.read())  # If parse() throws, f is never closed
    f.close()
    return data
```
**What to look for:** Resources (files, connections, sockets, locks) acquired without
`try/finally`, `with` statements, or `using` blocks.

---

## 7. Concurrency & Race Conditions

### Pattern 7.1: Check-Then-Act Race
**Frequency:** HIGH | **Severity:** CRITICAL

```python
# ❌ AI-GENERATED: Time-of-check to time-of-use (TOCTOU) race
if not Order.exists(order_id):           # Check: no order exists
    order = Order.create(order_id, data) # Act: create order
    # Between check and act, another request could create the same order
```
**What to look for:** Existence checks followed by creation. State checks followed by
state mutations. Missing unique constraints at the database level.

### Pattern 7.2: Shared Mutable State Without Synchronization
**Frequency:** MEDIUM | **Severity:** CRITICAL

```python
# ❌ AI-GENERATED: Global counter without thread safety
request_count = 0

async def handle_request():
    global request_count
    request_count += 1  # NOT atomic — data race on concurrent access
    await process()
```
**What to look for:** Global/module-level mutable variables. Class-level shared state.
Missing locks, atomics, or thread-safe data structures.

---

## 8. Data Integrity Issues

### Pattern 8.1: Missing Foreign Key Constraints
**Frequency:** MEDIUM | **Severity:** HIGH

```sql
-- ❌ AI-GENERATED: Referential integrity left to application code
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    author_id INTEGER,     -- No REFERENCES users(id)
    title VARCHAR(255)
    -- No CASCADE or SET NULL behavior defined
);
-- Application code can create posts referencing non-existent users
```
**What to look for:** Missing foreign key constraints. Missing NOT NULL on required
fields. No UNIQUE constraints where data uniqueness matters.

### Pattern 8.2: Inconsistent Denormalized Data
**Frequency:** MEDIUM | **Severity:** HIGH

```python
# ❌ AI-GENERATED: Updates order status but not the cached status
def cancel_order(order_id):
    order = Order.get(order_id)
    order.status = 'cancelled'
    order.save()
    # But order_items still have status='active'
    # And the user's cached order_count wasn't decremented
```
**What to look for:** Updates that modify one copy of data without updating related
caches, aggregates, or denormalized fields.

---

## 9. Configuration & Environment Assumptions

### Pattern 9.1: Environment-Specific Code Paths
**Frequency:** LOW | **Severity:** MEDIUM

```javascript
// ❌ AI-GENERATED: Different behavior in dev vs prod
if (process.env.NODE_ENV === 'development') {
    // Skip email verification in dev — but this check ships to prod
    user.verified = true;
}
```
**What to look for:** Environment checks that affect business logic. Debug-only code
that could leak. Feature flags without proper scoping.

### Pattern 9.2: Hardcoded Timeouts and Limits
**Frequency:** MEDIUM | **Severity:** MEDIUM

```python
# ❌ AI-GENERATED: Magic numbers without rationale
response = requests.get(url, timeout=30)    # Why 30?
cache.set(key, value, ttl=3600)             # Why 3600?
results = query.limit(100)                   # Why 100?
```
**What to look for:** Unexplained numeric constants. Missing configuration for tunable
parameters. Timeouts that don't consider operation characteristics.

---

## 10. Testing Blind Spots

### Pattern 10.1: Self-Validating Tests
**Frequency:** HIGH | **Severity:** HIGH

```python
# ❌ AI-GENERATED: Test that only checks the mock, not real behavior
def test_process_order(mocker):
    mock_save = mocker.patch('order_service.save')
    process_order(test_order)
    assert mock_save.called  # "Test" passes but doesn't validate anything real
```
**What to look for:** Tests that only verify mocks were called. Missing assertions on
actual outputs. Tests that can't fail (always green).

### Pattern 10.2: Missing Failure Test Cases
**Frequency:** VERY HIGH | **Severity:** MEDIUM

```python
# ❌ AI-GENERATED: 12 test cases, all happy path
def test_create_user_success():
    # ... only success case
def test_create_user_with_valid_email():
    # ... another success case
def test_create_user_with_profile():
    # ... another success case
# Missing: duplicate email, invalid email, missing required fields,
#          database failure, network timeout, concurrent creation
```
**What to look for:** Test suites with high coverage but no failure/error test cases.
Happy-path-only testing. Missing edge case tests.

---

## How to Use This Catalog During Verification

1. **Skim before starting.** Read through the pattern categories to prime your detection.

2. **Cross-reference as you audit.** For each dimension of verification, ask: "Which of
   these patterns apply to the code I'm looking at?"

3. **Don't pattern-match blindly.** The catalog teaches you WHAT to look for, but each
   codebase is different. Use judgment.

4. **Cite patterns in your report.** When you find an issue matching a catalog pattern,
   reference it: "This matches Pattern 4.1 (N+1 Query) — see the database query inside
   the loop at line 23."

5. **Add new patterns.** If you discover a bug pattern not in this catalog, note it.
   The catalog grows with experience.
