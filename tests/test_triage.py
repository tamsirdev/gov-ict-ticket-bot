from ai_triage import triage_issue_free


def test_hardware():
    cat, pri = triage_issue_free("My printer is jammed and smoking")
    assert cat == "Hardware"


def test_network():
    cat, pri = triage_issue_free("WiFi keeps disconnecting every 5 minutes")
    assert cat == "Network"


def test_account():
    cat, pri = triage_issue_free("I forgot my password and cannot login")
    assert cat == "Account"


def test_software():
    cat, pri = triage_issue_free("Excel crashes whenever I open a file")
    assert cat == "Software"


def test_general():
    cat, pri = triage_issue_free("I need help with something")
    assert cat == "General"


def test_critical_priority():
    cat, pri = triage_issue_free("The entire network is down, emergency!")
    assert pri == "Critical"


def test_high_priority():
    cat, pri = triage_issue_free("I am unable to work, this is blocking my team")
    assert pri == "High"


def test_low_priority():
    cat, pri = triage_issue_free("Just a quick question about how to reset my password")
    assert pri == "Low"


def test_medium_priority_default():
    cat, pri = triage_issue_free("The system is working but could be faster")
    assert pri == "Medium"
