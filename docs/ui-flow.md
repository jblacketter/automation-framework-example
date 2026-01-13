# UI Testing Flow

This document visualizes the UI test execution flow, browser lifecycle, and page object interactions.

## UI Test Execution Flow

```mermaid
sequenceDiagram
    participant B as Behave Runner
    participant E as Environment Hooks
    participant S as Step Definitions
    participant PO as Page Objects
    participant BF as BrowserFactory
    participant PW as Playwright
    participant UI as Web Application

    B->>E: before_all()
    Note over E: Initialize Config

    B->>E: before_feature()
    Note over E: Check @ui tag
    E->>BF: initialize()
    BF->>PW: sync_playwright().start()
    PW->>PW: Launch browser
    Note over PW: chromium/firefox/webkit

    B->>E: before_scenario()
    E->>BF: new_page()
    BF->>PW: Create context + page

    B->>S: Execute Given step
    S->>PO: navigate()
    PO->>UI: page.goto(url)
    UI-->>PO: Page loaded

    B->>S: Execute When step
    S->>PO: interact with page
    PO->>UI: click/fill/etc

    B->>S: Execute Then step
    S->>PO: assert state
    PO->>UI: Check elements

    B->>E: after_scenario()
    Note over E: Screenshot on failure
    E->>BF: close_context()

    B->>E: after_feature()
    E->>BF: close()
    BF->>PW: Close browser

    B->>E: after_all()
```

## Browser Lifecycle Management

```mermaid
flowchart TD
    subgraph "Feature Level"
        F_START([Feature Start]) --> INIT[BrowserFactory.initialize]
        INIT --> LAUNCH[Launch Browser]
        LAUNCH --> F_READY[Browser Ready]
        F_READY --> SCENARIOS
        SCENARIOS --> F_END[BrowserFactory.close]
        F_END --> F_STOP([Feature End])
    end

    subgraph SCENARIOS[Scenarios]
        direction TB
        S1_START([Scenario 1]) --> S1_CTX[New Context]
        S1_CTX --> S1_PAGE[New Page]
        S1_PAGE --> S1_TEST[Run Test]
        S1_TEST --> S1_CLOSE[Close Context]
        S1_CLOSE --> S1_END([Scenario End])

        S2_START([Scenario 2]) --> S2_CTX[New Context]
        S2_CTX --> S2_PAGE[New Page]
        S2_PAGE --> S2_TEST[Run Test]
        S2_TEST --> S2_CLOSE[Close Context]
        S2_CLOSE --> S2_END([Scenario End])
    end

    style LAUNCH fill:#4caf50,color:#fff
    style F_END fill:#f44336,color:#fff
```

## Page Object Model Flow

```mermaid
flowchart LR
    subgraph "Step Definition"
        STEP[ui_steps.py]
    end

    subgraph "Page Objects"
        BASE[BasePage]
        HOME[HomePage]
        ADMIN[AdminPage]
        BOOK[BookingPage]
    end

    subgraph "Playwright"
        PAGE[page]
        LOC[locator]
        ACTION[click/fill/etc]
    end

    subgraph "Browser"
        DOM[DOM Elements]
    end

    STEP --> HOME
    STEP --> ADMIN
    STEP --> BOOK

    HOME --> BASE
    ADMIN --> BASE
    BOOK --> BASE

    BASE --> PAGE
    PAGE --> LOC
    LOC --> ACTION
    ACTION --> DOM
```

## Page Navigation Flow

```mermaid
flowchart TD
    START([Navigate]) --> BUILD[Build Full URL]
    BUILD --> GOTO[page.goto]
    GOTO --> WAIT[Wait for Load State]
    WAIT --> NETWORK{Network Idle?}

    NETWORK -->|Yes| READY[Page Ready]
    NETWORK -->|Timeout| ERROR[Navigation Error]

    READY --> INTERACT[Interact with Page]
    ERROR --> SCREENSHOT[Take Screenshot]
    SCREENSHOT --> FAIL[Test Fails]

    style START fill:#2196f3,color:#fff
    style READY fill:#4caf50,color:#fff
    style FAIL fill:#f44336,color:#fff
```

## Element Interaction Pattern

```mermaid
sequenceDiagram
    participant T as Test Step
    participant P as Page Object
    participant B as BasePage
    participant PW as Playwright

    T->>P: fill_contact_form(data)

    P->>B: scroll_to(CONTACT_NAME)
    B->>PW: locator.scroll_into_view()

    P->>B: fill(CONTACT_NAME, name)
    B->>PW: page.fill(selector, value)

    P->>B: fill(CONTACT_EMAIL, email)
    B->>PW: page.fill(selector, value)

    P->>B: fill(CONTACT_PHONE, phone)
    B->>PW: page.fill(selector, value)

    P->>B: click(SUBMIT_BUTTON)
    B->>PW: page.click(selector)

    P-->>T: Return self (chaining)
```

## Screenshot on Failure Flow

```mermaid
flowchart TD
    SCENARIO[Scenario Execution] --> STATUS{Scenario<br/>Status?}

    STATUS -->|passed| CLEANUP[Normal Cleanup]
    STATUS -->|failed| CHECK{Screenshot<br/>Enabled?}

    CHECK -->|Yes| CAPTURE[Capture Screenshot]
    CHECK -->|No| LOG_ONLY[Log Error Only]

    CAPTURE --> NAME[Generate Filename<br/>failure_scenario_timestamp.png]
    NAME --> SAVE[Save to reports/screenshots/]
    SAVE --> LOG[Log Screenshot Path]
    LOG --> DETAILS[Log Failure Details]
    DETAILS --> CLEANUP

    LOG_ONLY --> DETAILS

    style SCENARIO fill:#2196f3,color:#fff
    style CAPTURE fill:#ff9800,color:#fff
```

## Home Page Test Flow

```mermaid
flowchart TD
    subgraph "Given: I am on the home page"
        G1[Create HomePage object]
        G2[Navigate to URL]
        G3[Wait for page load]
    end

    subgraph "Then: Assertions"
        T1[Assert hotel name visible]
        T2[Assert rooms displayed]
        T3[Assert contact form visible]
    end

    G1 --> G2 --> G3 --> T1 --> T2 --> T3

    style G1 fill:#4caf50,color:#fff
    style T3 fill:#2196f3,color:#fff
```

## Contact Form Submission Flow

```mermaid
sequenceDiagram
    participant T as Test
    participant H as HomePage
    participant PW as Playwright
    participant UI as Website

    T->>H: fill_contact_form(data)

    H->>PW: scroll_to(form)
    PW->>UI: Scroll

    H->>PW: fill(name)
    H->>PW: fill(email)
    H->>PW: fill(phone)
    H->>PW: fill(subject)
    H->>PW: fill(message)

    T->>H: submit_contact_form()
    H->>PW: click(submit)
    PW->>UI: Submit form
    UI-->>PW: Response

    T->>H: is_contact_success_visible()
    H->>PW: is_visible(success_message)
    PW-->>H: true/false
    H-->>T: Result
```

## Admin Login Flow

```mermaid
flowchart TD
    START([Start]) --> NAV[Navigate to Admin Page]
    NAV --> WAIT[Wait for Login Form]
    WAIT --> FILL[Fill Username & Password]
    FILL --> SUBMIT[Click Login Button]
    SUBMIT --> CHECK{Login<br/>Successful?}

    CHECK -->|Yes| LOGGED[Logged In State]
    CHECK -->|No| ERROR[Error Message Displayed]

    LOGGED --> LOGOUT[Logout Available]
    ERROR --> RETRY[Can Retry]

    style START fill:#4caf50,color:#fff
    style LOGGED fill:#2196f3,color:#fff
    style ERROR fill:#f44336,color:#fff
```

## Booking Calendar Interaction

```mermaid
flowchart LR
    subgraph "Calendar Actions"
        OPEN[Open Calendar]
        NAV_MONTH[Navigate Month]
        SELECT[Select Dates]
        CONFIRM[Confirm Selection]
    end

    subgraph "Guest Details"
        FIRST[First Name]
        LAST[Last Name]
        EMAIL[Email]
        PHONE[Phone]
    end

    subgraph "Booking"
        SUBMIT[Submit]
        SUCCESS[Confirmation]
        FAIL[Error]
    end

    OPEN --> NAV_MONTH --> SELECT --> CONFIRM
    CONFIRM --> FIRST --> LAST --> EMAIL --> PHONE
    PHONE --> SUBMIT
    SUBMIT --> SUCCESS
    SUBMIT --> FAIL
```

## Locator Strategy

```mermaid
graph TD
    subgraph "Locator Patterns"
        ID[ID Selector<br/>#element-id]
        CSS[CSS Selector<br/>.class-name]
        TEXT[Text Selector<br/>text='Click me']
        ROLE[Role Selector<br/>role=button]
        COMBO[Combined<br/>Multiple fallbacks]
    end

    subgraph "Priority Order"
        P1[1. ID - Most stable]
        P2[2. data-testid - Test specific]
        P3[3. CSS Class - Common]
        P4[4. Text content - User facing]
    end

    ID --> P1
    CSS --> P3
    TEXT --> P4

    style P1 fill:#4caf50,color:#fff
    style P2 fill:#8bc34a,color:#fff
```

## Assertions Flow

```mermaid
flowchart TD
    ASSERT[Make Assertion] --> TYPE{Assertion Type}

    TYPE -->|Visibility| VIS[expect.to_be_visible]
    TYPE -->|Text| TXT[expect.to_have_text]
    TYPE -->|Value| VAL[expect.to_have_value]
    TYPE -->|URL| URL[expect.to_have_url]
    TYPE -->|Count| CNT[locator.count]

    VIS --> WAIT_VIS[Auto-wait for visibility]
    TXT --> WAIT_TXT[Auto-wait for text]
    VAL --> WAIT_VAL[Auto-wait for value]
    URL --> WAIT_URL[Auto-wait for URL]
    CNT --> CHECK_CNT[Check count]

    WAIT_VIS --> PASS_FAIL{Result}
    WAIT_TXT --> PASS_FAIL
    WAIT_VAL --> PASS_FAIL
    WAIT_URL --> PASS_FAIL
    CHECK_CNT --> PASS_FAIL

    PASS_FAIL -->|Pass| CONTINUE[Continue Test]
    PASS_FAIL -->|Fail| THROW[Throw AssertionError]

    style CONTINUE fill:#4caf50,color:#fff
    style THROW fill:#f44336,color:#fff
```
