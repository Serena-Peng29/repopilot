from repopilot.eval.scoring import score_patch


def test_score_patch_identifies_small_low_risk_patch() -> None:
    diff = """diff --git a/calculator.py b/calculator.py
index 1344080..e1829c3 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def add(a: int, b: int) -> int:
-    return a - b
+    return a + b
"""

    score = score_patch(diff)

    assert score.changed_files == 1
    assert score.additions == 1
    assert score.deletions == 1
    assert score.risk_level == "low"
    assert score.risk_reasons == ["small focused patch"]


def test_score_patch_flags_sensitive_and_test_files() -> None:
    diff = """diff --git a/auth/session.py b/auth/session.py
index 1111111..2222222 100644
--- a/auth/session.py
+++ b/auth/session.py
@@ -1 +1 @@
-token = "old"
+token = "new"
diff --git a/tests/test_session.py b/tests/test_session.py
index 3333333..4444444 100644
--- a/tests/test_session.py
+++ b/tests/test_session.py
@@ -1 +1 @@
-assert False
+assert True
"""

    score = score_patch(diff)

    assert score.risk_level == "high"
    assert "auth/session.py" in score.sensitive_files
    assert "tests/test_session.py" in score.test_files
    assert "touches high-sensitivity files" in score.risk_reasons
    assert "modifies test files" in score.risk_reasons
    assert "possible test weakening" in score.risk_reasons


def test_score_patch_flags_dependency_and_ci_files() -> None:
    diff = """diff --git a/package.json b/package.json
index 1111111..2222222 100644
--- a/package.json
+++ b/package.json
@@ -1 +1 @@
-{"dependencies": {}}
+{"dependencies": {"left-pad": "1.3.0"}}
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 3333333..4444444 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -1 +1 @@
-run: npm test
+run: npm test -- --runInBand
"""

    score = score_patch(diff)

    assert score.risk_level == "medium"
    assert "changes dependency files" in score.risk_reasons
    assert "changes CI configuration" in score.risk_reasons


def test_score_patch_flags_migration_as_high_risk() -> None:
    diff = """diff --git a/migrations/001_drop_users.sql b/migrations/001_drop_users.sql
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/migrations/001_drop_users.sql
@@ -0,0 +1 @@
+DROP TABLE users;
"""

    score = score_patch(diff)

    assert score.risk_level == "high"
    assert "changes database migrations" in score.risk_reasons


def test_score_patch_flags_test_weakening() -> None:
    diff = """diff --git a/tests/test_calculator.py b/tests/test_calculator.py
index 1111111..2222222 100644
--- a/tests/test_calculator.py
+++ b/tests/test_calculator.py
@@ -1 +1,2 @@
-assert add(2, 3) == 5
+# assert add(2, 3) == 5
+assert True
"""

    score = score_patch(diff)

    assert score.risk_level == "high"
    assert "possible test weakening" in score.risk_reasons
