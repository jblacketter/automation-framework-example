# Framework Architecture

This document provides a visual overview of the test automation framework architecture using Mermaid diagrams.

## High-Level Architecture

```mermaid
graph TB
    subgraph "Test Layer"
        F[Feature Files<br/>*.feature]
        S[Step Definitions<br/>steps/]
    end

    subgraph "Business Layer"
        SVC[Services<br/>auth, booking, room]
        PO[Page Objects<br/>home, admin, booking]
    end

    subgraph "Core Layer"
        API[APIClient<br/>Singleton]
        BF[BrowserFactory<br/>Singleton]
        CFG[Config<br/>Singleton]
        LOG[Logger]
        VAL[ResponseValidator]
    end

    subgraph "External Systems"
        UI[UI Application<br/>automationintesting.online]
        REST[REST API<br/>restful-booker.herokuapp.com]
    end

    F --> S
    S --> SVC
    S --> PO
    SVC --> API
    SVC --> VAL
    PO --> BF
    API --> CFG
    BF --> CFG
    API --> LOG
    BF --> LOG
    API --> REST
    BF --> UI
```

## Component Dependencies

```mermaid
graph LR
    subgraph "Core Components"
        C[Config]
        L[Logger]
        A[APIClient]
        B[BrowserFactory]
        V[ResponseValidator]
    end

    A --> C
    A --> L
    B --> C
    B --> L
    V --> A

    style C fill:#e1f5fe
    style L fill:#e1f5fe
    style A fill:#fff3e0
    style B fill:#fff3e0
    style V fill:#f3e5f5
```

## Singleton Pattern Implementation

```mermaid
classDiagram
    class Config {
        -_instance: Config
        -_initialized: bool
        +get(key, default)
        +get_required(key)
        +get_int(key, default)
        +get_bool(key, default)
        +base_url: str
        +api_base_url: str
        +browser: str
        +headless: bool
    }

    class APIClient {
        -_instance: APIClient
        -_initialized: bool
        -session: Session
        -_token: str
        +set_token(token)
        +clear_token()
        +get(endpoint)
        +post(endpoint, json)
        +put(endpoint, json)
        +delete(endpoint)
    }

    class BrowserFactory {
        -_instance: BrowserFactory
        -_playwright: Playwright
        -_browser: Browser
        -_page: Page
        +initialize()
        +new_page()
        +take_screenshot(name)
        +close()
    }

    Config --> APIClient : provides config
    Config --> BrowserFactory : provides config
```

## Page Object Model Structure

```mermaid
classDiagram
    class BasePage {
        <<abstract>>
        +page: Page
        +config: Config
        +logger: Logger
        +url_path: str*
        +navigate()
        +click(selector)
        +fill(selector, value)
        +get_text(selector)
        +is_visible(selector)
        +wait_for_element(selector)
        +take_screenshot(name)
    }

    class HomePage {
        +HOTEL_NAME: str
        +ROOM_CARD: str
        +CONTACT_FORM: str
        +get_hotel_name()
        +get_room_count()
        +fill_contact_form()
        +submit_contact_form()
    }

    class AdminPage {
        +LOGIN_USERNAME: str
        +LOGIN_PASSWORD: str
        +login(username, password)
        +login_as_admin()
        +logout()
        +is_logged_in()
        +create_room()
    }

    class BookingPage {
        +CALENDAR: str
        +GUEST_FORM: str
        +select_dates()
        +fill_guest_details()
        +submit_booking()
    }

    BasePage <|-- HomePage
    BasePage <|-- AdminPage
    BasePage <|-- BookingPage
```

## Service Layer Architecture

```mermaid
classDiagram
    class AuthService {
        -client: APIClient
        -config: Config
        +login(username, password)
        +login_as_admin()
        +validate_token()
        +logout()
    }

    class BookingService {
        -client: APIClient
        +get_all_bookings()
        +get_booking(id)
        +create_booking(...)
        +update_booking(...)
        +delete_booking(id)
        +create_test_booking()
    }

    class RoomService {
        -client: APIClient
        +get_all_rooms()
        +get_room(id)
        +create_room(...)
        +update_room(...)
        +delete_room(id)
    }

    AuthService --> APIClient
    BookingService --> APIClient
    RoomService --> APIClient
```

## Directory Structure

```mermaid
graph TD
    ROOT[automation-framework/]

    ROOT --> CORE[core/]
    ROOT --> SVC[services/]
    ROOT --> PAGES[pages/]
    ROOT --> FEAT[features/]
    ROOT --> STEPS[steps/]
    ROOT --> DOCS[docs/]
    ROOT --> GH[.github/]
    ROOT --> ENV[environment.py]

    CORE --> C1[api_client.py]
    CORE --> C2[browser_factory.py]
    CORE --> C3[config.py]
    CORE --> C4[logger.py]
    CORE --> C5[response_validator.py]

    SVC --> S1[auth_service.py]
    SVC --> S2[booking_service.py]
    SVC --> S3[room_service.py]

    PAGES --> P1[base_page.py]
    PAGES --> P2[home_page.py]
    PAGES --> P3[admin_page.py]
    PAGES --> P4[booking_page.py]

    FEAT --> FA[api/]
    FEAT --> FU[ui/]

    FA --> FA1[auth.feature]
    FA --> FA2[bookings.feature]

    FU --> FU1[home.feature]
    FU --> FU2[admin.feature]
    FU --> FU3[booking.feature]

    style ROOT fill:#e8f5e9
    style CORE fill:#e3f2fd
    style SVC fill:#fff3e0
    style PAGES fill:#fce4ec
    style FEAT fill:#f3e5f5
```

## Test Execution Layers

```mermaid
graph TB
    subgraph "Execution Flow"
        direction TB
        BEHAVE[Behave Runner]
        HOOKS[Environment Hooks]
        FEATURES[Feature Files]
        STEPS[Step Definitions]
        BIZ[Business Layer]
        CORE[Core Layer]
        EXT[External Systems]
    end

    BEHAVE --> HOOKS
    HOOKS --> FEATURES
    FEATURES --> STEPS
    STEPS --> BIZ
    BIZ --> CORE
    CORE --> EXT

    style BEHAVE fill:#4caf50,color:#fff
    style HOOKS fill:#2196f3,color:#fff
    style FEATURES fill:#9c27b0,color:#fff
    style STEPS fill:#ff9800,color:#fff
    style BIZ fill:#f44336,color:#fff
    style CORE fill:#607d8b,color:#fff
```
