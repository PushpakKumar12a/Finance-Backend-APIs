## Entity-Relationship (ER) Diagram
This diagram shows the database models and their relationships.

```mermaid
erDiagram
    User ||--o{ Record : "has many"
    
    User {
        int id PK
        string email "Unique Identifier"
        string username
        string password
        string first_name
        string last_name
        string role "Choices: viewer, analyst, admin"
        boolean is_active
        boolean is_staff
        boolean is_superuser
        datetime last_login
        datetime date_joined
    }
    
    Record {
        int id PK
        int user_id FK
        decimal amt "Transaction amount"
        string type "Choices: income, expense"
        string cat "Category label"
        date date
        string desc
        boolean del_flag "Soft delete flag"
        datetime created_at
        datetime updated_at
    }
```

## High-Level Architecture
This diagram outlines the major components and the flow of the application.

```mermaid
graph TD
    Client[Client / Web Browser] --> API[Django Backend APIs]
    
    subgraph Django Project [Finance Backend System]
        API --> AccountsApp[Accounts App]
        API --> RecordsApp[Records App]
        API --> DashboardApp[Dashboard App]
        
        AccountsApp -.-> |"Manages Auth & Roles"| Models(Models)
        RecordsApp -.-> |"CRUD Financial Records"| Models
        DashboardApp -.-> |"Data Aggregation"| Models
        
        Models --> DB[(Database)]
    end
```

## API Flow Sequence Diagram
This diagram illustrates the request-response lifecycle for typical flows: Authentication, Managing Records, Fetching Dashboard Analytics, and Admin Operations.

```mermaid
sequenceDiagram
    participant Client
    participant AuthAPI as Auth API (/api/auth)
    participant RecordsAPI as Records API (/api/records)
    participant DashboardAPI as Dashboard API (/api/dashboard)
    participant UserAPI as User API (/api/users)
    participant DB as MySQL Database
    
    %% Authentication Flow
    Note over Client,DB: 1. Authentication Flow
    
    Client->>+AuthAPI: POST /api/auth/register/ (User details)
    AuthAPI->>DB: Insert new User
    DB-->>AuthAPI: User created
    AuthAPI-->>-Client: 201 Created
    
    Client->>+AuthAPI: POST /api/auth/login/ (Credentials)
    AuthAPI->>DB: Validate credentials
    DB-->>AuthAPI: Match successful
    AuthAPI-->>-Client: 200 OK (Access & Refresh JWT)
    
    %% Records Flow
    Note over Client,DB: 2. Financial Records Flow (Requires JWT)
    
    Client->>+RecordsAPI: POST /api/records/ (amt, type, cat) + Bearer Token
    RecordsAPI->>AuthAPI: Authenticate & Identify User
    RecordsAPI->>DB: Save FinancialRecord
    DB-->>RecordsAPI: Record saved
    RecordsAPI-->>-Client: 201 Created (Record details)
    
    Client->>+RecordsAPI: GET /api/records/ + Bearer Token
    RecordsAPI->>DB: Fetch Active Records for User
    DB-->>RecordsAPI: Queryset of Records
    RecordsAPI-->>-Client: 200 OK (Paginated records)
    
    %% Dashboard Flow
    Note over Client,DB: 3. Analytics & Dashboard Flow (Requires JWT)
    
    Client->>+DashboardAPI: GET /api/dashboard/summary/ + Bearer Token
    DashboardAPI->>DB: Aggregate user amounts (income/expense)
    DB-->>DashboardAPI: Summarized Data
    DashboardAPI-->>-Client: 200 OK (Total Income, Expense, Balance)
    
    Client->>+DashboardAPI: GET /api/dashboard/category-breakdown/ + Bearer Token
    DashboardAPI->>DB: Group expenses by category
    DB-->>DashboardAPI: Category aggregated data
    DashboardAPI-->>-Client: 200 OK (Category statistics)
    
    %% Admin Flow
    Note over Client,DB: 4. Admin Management Flow (Requires Admin Role)
    
    Client->>+UserAPI: GET /api/users/ + Bearer Token
    UserAPI->>DB: Check User Role is_admin_role
    DB-->>UserAPI: Verified Admin
    UserAPI->>DB: Fetch all system users
    DB-->>UserAPI: List of Users
    UserAPI-->>-Client: 200 OK (Users List)
```

## Role-Based Access Control (RBAC) Flow
This matrix illustrates the permission levels defined for the three user tiers: [Viewer](file:///d:/coding/Django/accounts/permissions.py#38-43), [Analyst](file:///d:/coding/Django/accounts/permissions.py#27-36), and [Admin](file:///d:/coding/Django/accounts/permissions.py#16-25). Each role inherently inherits the permissions of the roles below it.

```mermaid
graph TD
    Admin((Admin))
    Analyst((Analyst))
    Viewer((Viewer))
    
    subgraph Dashboard Analytics API
        DashGET[GET /api/dashboard/*]
    end
    
    subgraph Records API
        RecGET[GET /api/records/]
        RecWRITE[POST, PATCH, DELETE /api/records/]
    end
    
    subgraph Auth API
        Login[Auth & JWT /api/auth/*]
    end
    
    %% Base Permissions
    Viewer --> |Authentication| Login
    Viewer --> |Read-only Access| RecGET
    
    %% Analyst Permissions (Inherits Viewer)
    Analyst --> |Inherits Viewer Permissions| Viewer
    Analyst --> |View Analytics| DashGET
    
    %% Admin Permissions (Inherits Analyst)
    Admin --> |Inherits Analyst Permissions| Analyst
    Admin --> |Modify Financial Records| RecWRITE
```
