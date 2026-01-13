# API Testing Flow

This document visualizes the API test execution flow and request/response lifecycle.

## API Test Execution Flow

```mermaid
sequenceDiagram
    participant B as Behave Runner
    participant E as Environment Hooks
    participant S as Step Definitions
    participant SVC as Service Layer
    participant API as APIClient
    participant EXT as External API

    B->>E: before_all()
    Note over E: Initialize Config, Logger

    B->>E: before_feature()
    Note over E: Log feature start

    B->>E: before_scenario()
    Note over E: Reset API client state
    Note over E: Clear tokens/cookies

    B->>S: Execute Given step
    S->>SVC: Call service method
    SVC->>API: Make HTTP request
    API->>EXT: Send request
    EXT-->>API: Return response
    API-->>SVC: Return response + validator
    SVC-->>S: Return result

    B->>S: Execute When step
    S->>SVC: Call service method
    SVC->>API: Make HTTP request
    API->>EXT: Send request
    EXT-->>API: Return response
    API-->>SVC: Return response + validator

    B->>S: Execute Then step
    S->>S: Assert with ResponseValidator

    B->>E: after_scenario()
    Note over E: Cleanup test data
    Note over E: Clear tokens

    B->>E: after_feature()
    B->>E: after_all()
```

## Authentication Flow

```mermaid
flowchart TD
    START([Start Test]) --> AUTH{Need Auth?}

    AUTH -->|Yes| LOGIN[AuthService.login]
    AUTH -->|No| EXEC[Execute Test]

    LOGIN --> POST[POST /auth]
    POST --> RESP{Response OK?}

    RESP -->|200| TOKEN[Extract Token]
    RESP -->|Other| FAIL[Auth Failed]

    TOKEN --> SET[APIClient.set_token]
    SET --> EXEC

    EXEC --> CLEANUP[Cleanup]
    CLEANUP --> CLEAR[Clear Token]
    CLEAR --> END([End Test])

    FAIL --> END

    style START fill:#4caf50,color:#fff
    style END fill:#f44336,color:#fff
    style TOKEN fill:#2196f3,color:#fff
```

## Booking CRUD Operations

```mermaid
flowchart LR
    subgraph "Create"
        C1[POST /booking] --> C2[201 Created]
        C2 --> C3[Return bookingid]
    end

    subgraph "Read"
        R1[GET /booking] --> R2[200 OK]
        R2 --> R3[Return list]
        R4[GET /booking/:id] --> R5[200 OK]
        R5 --> R6[Return booking]
    end

    subgraph "Update"
        U1[PUT /booking/:id] --> U2{Authenticated?}
        U2 -->|Yes| U3[200 OK]
        U2 -->|No| U4[403 Forbidden]
    end

    subgraph "Delete"
        D1[DELETE /booking/:id] --> D2{Authenticated?}
        D2 -->|Yes| D3[201 Created]
        D2 -->|No| D4[403 Forbidden]
    end
```

## Request/Response Lifecycle

```mermaid
sequenceDiagram
    participant Test as Test Step
    participant SVC as BookingService
    participant API as APIClient
    participant LOG as Logger
    participant VAL as ResponseValidator
    participant EXT as REST API

    Test->>SVC: create_booking(data)
    SVC->>API: post("/booking", json=data)

    API->>LOG: Log request (masked)
    Note over LOG: Mask sensitive data<br/>(passwords, tokens)

    API->>EXT: HTTP POST
    EXT-->>API: HTTP Response

    API->>LOG: Log response (truncated)
    API-->>SVC: Response object

    SVC->>VAL: Create validator
    SVC-->>Test: (Response, Validator)

    Test->>VAL: assert_status_code(200)
    Test->>VAL: assert_json_field("bookingid")
    VAL-->>Test: Assertions pass/fail
```

## API Error Handling

```mermaid
flowchart TD
    REQ[Make Request] --> RESP{Response Status}

    RESP -->|2xx| SUCCESS[Success Path]
    RESP -->|4xx| CLIENT[Client Error]
    RESP -->|5xx| SERVER[Server Error]

    SUCCESS --> PARSE[Parse JSON]
    PARSE --> VALIDATE[Validate Response]
    VALIDATE --> RETURN[Return to Test]

    CLIENT -->|401/403| AUTH_ERR[Authentication Error]
    CLIENT -->|404| NOT_FOUND[Not Found Error]
    CLIENT -->|400| BAD_REQ[Bad Request]

    SERVER --> RETRY{Retry?}
    RETRY -->|Yes, < 3| REQ
    RETRY -->|No| FAIL[Test Fails]

    AUTH_ERR --> ASSERT[Assert Expected]
    NOT_FOUND --> ASSERT
    BAD_REQ --> ASSERT
    ASSERT --> RETURN

    style SUCCESS fill:#4caf50,color:#fff
    style FAIL fill:#f44336,color:#fff
```

## Test Data Cleanup Flow

```mermaid
flowchart TD
    SCENARIO[Scenario Execution] --> CREATE{Data Created?}

    CREATE -->|Yes| TRACK[Track in Context<br/>bookings_to_cleanup]
    CREATE -->|No| COMPLETE[Scenario Complete]

    TRACK --> COMPLETE
    COMPLETE --> AFTER[after_scenario hook]

    AFTER --> CHECK{Cleanup List<br/>Empty?}

    CHECK -->|No| AUTH[Login as Admin]
    CHECK -->|Yes| DONE[Done]

    AUTH --> LOOP[For each booking_id]
    LOOP --> DELETE[DELETE /booking/:id]
    DELETE --> NEXT{More items?}

    NEXT -->|Yes| LOOP
    NEXT -->|No| CLEAR[Clear cleanup list]
    CLEAR --> DONE

    style SCENARIO fill:#2196f3,color:#fff
    style DONE fill:#4caf50,color:#fff
```

## Response Validator Chain

```mermaid
graph LR
    V[ResponseValidator] --> A[assert_status_code]
    A --> B[assert_valid_json]
    B --> C[assert_json_field]
    C --> D[assert_field_exists]
    D --> E[get_field]

    subgraph "Chainable Methods"
        A
        B
        C
        D
    end

    subgraph "Extraction"
        E
    end

    style V fill:#9c27b0,color:#fff
```

## API Client Connection Pooling

```mermaid
graph TB
    subgraph "APIClient Singleton"
        SESSION[requests.Session]
        ADAPTER[HTTPAdapter]
        RETRY[Retry Strategy]
        HEADERS[Default Headers]
        TOKEN[Token Storage]
    end

    subgraph "Connection Pool"
        C1[Connection 1]
        C2[Connection 2]
        C3[Connection 3]
        CN[Connection N]
    end

    SESSION --> ADAPTER
    ADAPTER --> RETRY
    ADAPTER --> C1
    ADAPTER --> C2
    ADAPTER --> C3
    ADAPTER --> CN

    RETRY --> |500, 502, 503, 504| R[Retry up to 3x]

    style SESSION fill:#2196f3,color:#fff
    style RETRY fill:#ff9800,color:#fff
```
