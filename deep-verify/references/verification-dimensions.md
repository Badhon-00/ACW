# Six-Dimension Verification Framework

This is your verification playbook. Run EVERY dimension against the code you're auditing.
The dimensions are ordered by how commonly AI introduces bugs in each category.

## Dimension 1: Intent vs. Implementation

**Core question:** Does this code actually do what it claims to do?

AI often generates code that LOOKS like a solution to the stated problem but implements
something subtly different. This happens because AI fills gaps in specifications with
reasonable-sounding but wrong assumptions.

### Verification Checklist

- [ ] What does the PR/commit message say this code does?
- [ ] What does the documentation/comment say this code does?
- [ ] What does the code ACTUALLY do when you trace every path?
- [ ] Are there functions whose names don't match their behavior?
- [ ] Does the implementation solve the WHOLE problem or only the happy path?
- [ ] Are there "bonus features" — behavior not requested that could cause issues?
- [ ] For each function: if you only read the name and parameters, would you expect
      this implementation?

### Red Flags
- Function name says "validate" but implementation also mutates
- Method called `get_X` that has side effects
- Boolean flag `is_admin` checked only client-side
- "Helper" functions that do more than help
- Comments that describe different behavior than the code

### Method
1. Read the PR description, commit message, and any issue/ticket context
2. For each changed function, state what you EXPECT it to do based on naming
3. Trace through the actual implementation
4. Note every discrepancy between expected and actual behavior
5. Identify any missing functionality that the intent implies but code doesn't deliver

---

## Dimension 2: Edge Case Discovery

**Core question:** What happens when inputs are unusual, extreme, or malicious?

AI is trained on common patterns and writes for the happy path. Edge cases are where
AI-generated code most reliably fails.

### Verification Checklist

**Input extremes:**
- [ ] Null, undefined, None, nil
- [ ] Empty string, empty array, empty object
- [ ] Zero, negative numbers, MAX_INT, MIN_INT
- [ ] Very long strings, deeply nested objects
- [ ] Unicode, special characters, emoji
- [ ] SQL/HTML/JS in string inputs (injection)

**State extremes:**
- [ ] First-ever use (empty database, no cache)
- [ ] Massive data volumes (1M+ records)
- [ ] Rapid successive calls (race conditions)
- [ ] Concurrent modifications

**Operational extremes:**
- [ ] Network timeout or failure
- [ ] Database connection loss
- [ ] Disk full, out of memory
- [ ] Clock skew, timezone edge cases

**Business logic extremes:**
- [ ] Discount > 100%, negative prices
- [ ] Orders with zero items
- [ ] Users with no permissions
- [ ] Circular references in data

### Method
1. List every input parameter and variable
2. For each, identify the "normal" range and the extremes
3. Trace what happens at each extreme
4. Pay special attention to operations that could overflow, underflow, or divide by zero

---

## Dimension 3: Security Audit

**Core question:** Can this code be exploited?

AI generates "functional" code first and "secure" code only when explicitly asked.
This dimension catches the security holes that come from that priority ordering.

### Verification Checklist

**Injection vulnerabilities:**
- [ ] SQL queries use parameterized statements (NOT string interpolation)
- [ ] Shell commands use proper escaping (NOT string concatenation)
- [ ] HTML output is escaped (XSS prevention)
- [ ] LDAP/XML/JSON queries are properly parameterized

**Authentication & Authorization:**
- [ ] Every protected endpoint has auth checks
- [ ] Auth checks verify BOTH "are you logged in?" AND "are you allowed to do this?"
- [ ] User A cannot access User B's data by changing an ID
- [ ] Admin functions are separately authorized

**Data Protection:**
- [ ] Secrets/keys are NOT in source code
- [ ] Passwords are hashed (bcrypt/argon2, NOT MD5/SHA1)
- [ ] PII is encrypted at rest where required
- [ ] Logs don't contain sensitive data (passwords, tokens, SSNs)

**Input Validation:**
- [ ] All user inputs have server-side validation (not just client-side)
- [ ] File uploads check type, size, and content
- [ ] URL parameters are validated before use

### Method
1. Check every place user input enters the system
2. Trace the input through to where it's used
3. Verify proper sanitization/parameterization at each step
4. Check auth on every endpoint — especially "internal" ones

---

## Dimension 4: Performance Analysis

**Core question:** Will this code scale, or does it only work in development?

AI generates code optimized for clarity, not performance. What runs instantly with
5 test records can bring down a server with 500,000 real records.

### Verification Checklist

**Database Queries:**
- [ ] No queries inside loops (N+1 pattern)
- [ ] Queries use appropriate indices
- [ ] SELECT statements specify needed columns (not SELECT *)
- [ ] Large result sets use pagination or streaming
- [ ] JOIN conditions are on indexed columns

**Algorithmic Complexity:**
- [ ] No O(n²) or worse algorithms on unbounded inputs
- [ ] Sorting is done at the database level when possible
- [ ] Expensive computations are cached where appropriate

**Memory:**
- [ ] No loading entire tables into memory
- [ ] Large file processing uses streams, not buffers
- [ ] Caches have eviction policies and size limits

**Network:**
- [ ] External API calls have timeouts
- [ ] Multiple external calls could be parallelized
- [ ] Responses are compressed where appropriate

### Method
1. Identify the "hot path" — what code runs on every request?
2. Estimate data volumes in production (not development)
3. Trace the hot path with production-scale data in mind
4. Flag every O(n²) pattern and N+1 query

---

## Dimension 5: Business Logic Integrity

**Core question:** Does this code respect the rules of the business domain?

This is the hardest dimension. AI doesn't understand your business. It writes technically
correct code that violates business rules in ways that are invisible to linters and tests.

### Verification Checklist

**Financial Operations:**
- [ ] Money amounts use decimal types (NOT float/double)
- [ ] Payment operations are idempotent
- [ ] Transactions are atomic (all-or-nothing)
- [ ] Refund logic handles partial refunds correctly

**Data Consistency:**
- [ ] Updates maintain referential integrity
- [ ] Denormalized data is kept in sync
- [ ] Audit trails capture who did what and when
- [ ] Soft deletes don't break uniqueness constraints

**Business Rules:**
- [ ] Discounts don't stack unintentionally
- [ ] Inventory can't go negative
- [ ] Price changes don't affect existing orders
- [ ] User roles/permissions are enforced at every layer

**State Machines:**
- [ ] All state transitions are valid (e.g., pending→shipped, not pending→cancelled)
- [ ] Impossible states are prevented
- [ ] State changes are logged

### Method
1. Ask: "What business rules should this code enforce?"
2. For each rule, verify it's implemented correctly
3. Test boundary cases of business rules
4. Check that rules are enforced server-side, not just in UI

---

## Dimension 6: Error Handling & Resilience

**Core question:** What happens when things go wrong?

AI writes optimistic code. It assumes the happy path. Production is a constant stream of
things going wrong — networks failing, databases restarting, third parties timing out.

### Verification Checklist

**Error Coverage:**
- [ ] Every external call (API, DB, file I/O) has error handling
- [ ] Errors are caught at the appropriate level (not just top-level)
- [ ] Error messages don't leak sensitive information
- [ ] Validation errors are user-friendly

**Retry & Resilience:**
- [ ] External calls have retry logic with exponential backoff
- [ ] Circuit breaker pattern for unreliable dependencies
- [ ] Graceful degradation when optional services are down

**Logging & Observability:**
- [ ] Errors are logged with context (user, request ID, stack trace)
- [ ] Key operations log structured data for debugging
- [ ] Performance metrics are captured for critical paths

**Resource Management:**
- [ ] Files, connections, and locks are released in finally/with blocks
- [ ] Connection pools have appropriate sizes and timeouts
- [ ] Background tasks have error handling and monitoring

### Method
1. Trace every external call (database, API, file system, message queue)
2. For each call: "What if this fails? What if it's slow? What if it returns garbage?"
3. Check that errors propagate or are handled — never swallowed silently
4. Verify resources are cleaned up in all code paths (success, failure, and exception)
