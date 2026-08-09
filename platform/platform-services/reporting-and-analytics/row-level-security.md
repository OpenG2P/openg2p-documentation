# Passing Custom User Context in Row Level Security

Apache Superset Row Level Security (RLS) is a feature that restricts access to specific rows in a dataset, providing fine-grained control over data visibility. RLS is essential for enforcing data privacy, security, and multi-tenancy—so users see only the data relevant to them.

Passing custom user context into Row Level Security (RLS) in Apache Superset enables dynamic and personalized data access for each user. Instead of hardcoding filters or maintaining a large matrix of roles, the system can use real-time user attributes—such as region, district, or department—provided by the authentication provider.

### How It Works

When a user logs into Superset, their authentication token includes custom claims, like `"district"` or `"region"`. These claims are extracted by Superset’s security manager and attached to the user’s session. Through SQL templating and Jinja macros, these attributes become available for use in RLS filters within datasets.

For example, with a district claim present, a filter in Superset can use:

```
district_name = '{{ district() }}'
```

This filter adapts automatically to match the district of the currently logged-in user, ensuring that users can only see data relevant to them. This approach greatly simplifies configuration and maintenance, especially for environments with hundreds of data partitions or users.

### Implementation Steps <a href="#implementation-steps" id="implementation-steps"></a>

#### 1. Assign Custom Attributes in Keycloak

Start by adding user-specific attributes (such as `district`, `region`, or `department`) in the Keycloak. These attributes must be included as part of the user’s authentication token or their user info response.

#### 2. Extract Claims and Attach to Superset User

Configure Superset’s security manager—often by subclassing `SupersetSecurityManager` (or `CustomSsoSecurityManager`)—to extract claims from the authentication response. This should include your custom attributes and attach them to the Superset user context. For example:

```
from superset.security import SupersetSecurityManager

class CustomSsoSecurityManager(SupersetSecurityManager):
  def oauth_user_info(self, provider, response=None):
    if provider == "keycloak":
      me = self.appbuilder.sm.oauth_remotes[provider].get(
        "openid-connect/userinfo"
      )
      me.raise_for_status()
      data = me.json()

      return {
        ...
        "district": data.get("district", ""),
        ...
      }

    return {}  

  def auth_user_oauth(self, userinfo):
    user = super().auth_user_oauth(userinfo)
    if user and "district" in userinfo:
        session["district"] = userinfo["district"]
    return user

CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager
```

This makes attributes like `district` available for the currently authenticated user session.

#### 3. Register Jinja Macro for the Attribute

To utilize these attributes in RLS (and SQL templates), register a Jinja macro in your `superset_config.py` that fetches the current user's attribute:

```
# Enable Jinja template processing
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

from flask import session

def district():
    return session.get("district", "")

JINJA_CONTEXT_ADDONS = {
    "district": district,
}
```

This macro exposes the user's district so it can be referenced in your RLS filter definitions.

#### 4. Use the Attribute in RLS Filter

When configuring Row Level Security rules for datasets, use the Jinja macro in the SQL filter, for example:

```
district_name = '{{ district() }}'
```

This filter will dynamically insert the logged-in user's district, ensuring that data returned always matches the user's context.

#### 5. Validate the Configuration

* Test by logging in with users having different “district” values.
* In SQL Lab or a dashboard, run:

```
SELECT '{{ district() }}' as district_value
```

With these steps, you can ensure scalable, dynamic, and highly customizable RLS enforcement in Superset by leveraging user-specific attributes from Keycloak.
