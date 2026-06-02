# Tech Guides

### Persistent Entities in openg2p-spar-mapper-partner-api

#### id\_fa\_mappings&#x20;

Contains the records for id\_value (beneficiary Id) and fa\_value (Financial Address) mapping

| Column           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id\_value        | <p>This is the Beneficiary ID - that will travel in the G2P Chain. This the beneficiary id for which the upstream PBMS / MIS platforms will create disbursements<br><br>The id_value is constructed using a construction strategy (decided based on implementation). <br><br>If the mapper is maintained using the self service paradigm, one of the ways that you can construct the ID Value is using the "auth" attributes from the Login Provider. An OIDC / OAuth2.0 Login provider usually provides the following attributes</p><ul><li>sub - Subject. Usually the ID/Token of the Beneficiary</li><li>iss - Issuer URL</li><li>name - Name of Beneficiary</li><li>email - Email of Beneficiary</li><li>phone_number - Phone Number of Beneficiary<br></li></ul><p>If we decide that the Banks update the Mapper, then a suitable construction strategy needs to be arrived at.</p> |
| fa\_value        | <p>This is the Financial Address of the Beneficiary - Usually will represent the Savings/ Checking /Current account of the beneficiary in a Bank. <br><br>The fa_value should be the full account details, such that this value alone is sufficient to enable a payment transaction into the account using the National Clearing Network. </p>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| name             | <p>The name of the beneficiary. <br><br>It is a good idea to have the name of the beneficiary travel back to the upstream systems as part of the "disbursement settlement status" -- The Disbursement settlement status should be sent by the final destination bank (where the beneficiary is credited).</p>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| phone            | Phone number of the beneficiary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| additional\_info | <p>This is an extensibility feature - to store additional attributes required in an implementation.<br><br>The SPAR Beneficiary Portal populates this column with the strategy-Id (specifies the strategy used for constructing the fa_value)</p>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

### Persistent Entities in openg2p-spar-bene-portal-api

{% hint style="info" %}
From v2.0 the DFSP model was **simplified** to three entity types — **BANK**,
**BRANCH** and **WALLET-PROVIDER** (see `openg2p-spar-models`). The generic
`dfsp_levels` / `dfsp_level_values` hierarchy described below is retained here as
conceptual background; refer to the `openg2p-spar-models` package for the
authoritative, current schema.
{% endhint %}

dfsp\_level and dfsp\_level\_values - are static tables that contain the information pertaining to the Banks (and other financial service providers), their branches.  The use of these two tables are explained below using examples

#### dfsp\_levels

<table><thead><tr><th width="78">id</th><th width="227">name</th><th width="246">level_type - ENUM</th><th>parent</th></tr></thead><tbody><tr><td>1</td><td>Bank</td><td>bank</td><td>0</td></tr><tr><td>2</td><td>Branch</td><td>branch</td><td>1</td></tr><tr><td>3</td><td>Account number</td><td>account</td><td>2</td></tr></tbody></table>

The above data indicates that, to fully express the Financial Address of a Beneficiary's bank account, the self service platform needs to capture 3 attributes for the Financial Address, viz. Bank, Branch & Account

Similarly for a Mobile Number based Wallet, we can think of the following dfsp\_level configuration

<table><thead><tr><th width="61">id</th><th width="279">name</th><th width="224">level_type - ENUM</th><th>parent</th></tr></thead><tbody><tr><td>4</td><td>Mobile Wallet Service Provider</td><td>mobile_wallet_provider</td><td>0</td></tr><tr><td>5</td><td>Mobile number</td><td>mobile_number</td><td>5</td></tr></tbody></table>

For a Email Address based Wallet, we can have the following dfsp\_level configuration

<table><thead><tr><th width="61">id</th><th width="279">name</th><th width="224">level_type - ENUM</th><th>parent</th></tr></thead><tbody><tr><td>6</td><td>Email Wallet Service Provider</td><td>email_wallet_provider</td><td>0</td></tr><tr><td>7</td><td>Email address</td><td>email_address</td><td>6</td></tr></tbody></table>

A Beneficiary Portal front-end uses the api - "get\_levels (parent)" to paint the UI fields to capture the input for these attributes - parent = 0, will provide the first level for the FA hierarchy

<figure><img src="../../.gitbook/assets/self-service-ui-dfsp-levels.png" alt="" width="372"><figcaption><p>Beneficiary Portal - capture of FA information</p></figcaption></figure>

#### dfsp\_level\_values

For facilitating capture of a Bank Account, we can visualize the following dfsp\_level\_values configuration

<table><thead><tr><th width="66">id</th><th width="220">name</th><th width="177">code</th><th>parent</th><th>level_id</th></tr></thead><tbody><tr><td>1</td><td>Bank One</td><td>Bank001</td><td>0</td><td>1</td></tr><tr><td>2</td><td>Bank Two</td><td>Bank002</td><td>0</td><td>1</td></tr><tr><td>3</td><td>Bank Three</td><td>Bank003</td><td>0</td><td>1</td></tr></tbody></table>

The API - get\_level\_values (parent = 0, level\_id = 1) - will yield the UI a drop down of these 3 banks.

<table><thead><tr><th width="66">id</th><th width="141">name</th><th width="258">code</th><th width="97">parent</th><th>level_id</th></tr></thead><tbody><tr><td>1</td><td>Branch 001</td><td>Branch001-Bank001</td><td>1</td><td>2</td></tr><tr><td>2</td><td>Branch 002</td><td>Branch002-Bank001</td><td>1</td><td>2</td></tr><tr><td>3</td><td>Branch 003</td><td>Branch003-Bank001</td><td>1</td><td>2</td></tr></tbody></table>

The API - get\_level\_values (parent = 1, level\_id = 2) - will yield the UI a drop down of these 3 branches for Bank One

#### login\_providers

<table><thead><tr><th width="66">id</th><th width="102">name</th><th width="181">login_button_image_url</th><th width="245">authorization_parameters</th><th>strategy_id</th></tr></thead><tbody><tr><td>1</td><td>Keycloak</td><td>The image shown on the UI for the login provider</td><td></td><td>1</td></tr></tbody></table>

The API - get\_login\_providers - will provide the list of configured login\_providers. The UI can then redirect itself to the redirect\_url specified for that login\_provider for the necessary authentication.

### FA and ID Strategy

A **strategy** defines how a structured value — a Financial Address (FA) or an ID — is turned into the single string that is actually stored in the mapper, and how that string is parsed back into its fields. Strategies live in the `strategy` table; each row has:

| Column | Meaning |
| --- | --- |
| `id` | Integer primary key. **This is the value partner systems reference** (see below). |
| `strategy_type` | `ID` or `FA`. |
| `construct_strategy` | A **Python format string** with `{placeholders}`. Used to build the stored string. |
| `deconstruct_strategy` | A **regex with named capture groups** `(?P<name>…)`. Used to parse the stored string back into fields. |
| `description` | Human-readable label. |
| `active` | Whether the strategy is enabled. |

#### What "construct" and "deconstruct" mean

* **Construct** (structured → stored string): the service runs `construct_strategy.format(**fields)`. For a bank FA with fields `bank_code`, `branch_code`, `account_number`, … a construct string like

  ```
  account_number:{account_number}.branch_name:{branch_name}.branch_code:{branch_code}.bank_name:{bank_name}.bank_code:{bank_code}.fa_type:{fa_type}
  ```

  produces a single string such as `account_number:123.branch_name:Main.branch_code:BR2.bank_name:Bank One.bank_code:B1.fa_type:BANK`. The placeholder names must match the FA/ID field names.
* **Deconstruct** (stored string → structured): the service runs `re.match(deconstruct_strategy, value).groupdict()`. The regex is the mirror of the construct string, with each field captured by a named group, e.g.

  ```
  ^account_number:(?P<account_number>.*)\.branch_name:(?P<branch_name>.*)\.branch_code:(?P<branch_code>.*)\.bank_name:(?P<bank_name>.*)\.bank_code:(?P<bank_code>.*)\.fa_type:(?P<fa_type>.*)$
  ```

ID strategies work the same way, but the fields come from the login provider's auth claims (e.g. `sub`). For example construct `token:{sub}@nationalId` with deconstruct `^token:(?P<sub>.[^.]*)@nationalId$`.

#### How a strategy is used by the APIs

The link / update request carries an `fa` object that includes a `strategy_id`. The Mapper Partner API (and the Beneficiary Portal API) then:

1. reads that strategy and **constructs** the FA string for storage,
2. records the `strategy_id` in the mapping's `additional_info`,
3. on **resolve**, reads `strategy_id` back and **deconstructs** the stored string into fields for the response.

Because the integer `id` is what callers send in `fa.strategy_id`, the ids must be **stable and identical across all environments**.

{% hint style="danger" %}
**Never delete (or change) a strategy once it has been used.** Existing mappings were stored using a strategy's `construct_strategy`, and `resolve` depends on the *same* strategy's `deconstruct_strategy` regex to parse them back. Deleting a strategy — or editing its construct/deconstruct after data exists — will break `resolve` for every FA stored with it. To evolve behaviour, **add a new strategy with a new `id`**; treat strategies as append-only and immutable.
{% endhint %}

#### Default strategies

A standard SPAR install seeds four strategies (id 1–4): an `ID` strategy (Keycloak) and three `FA` strategies (Bank, Email wallet, Phone/mobile wallet). These are provisioned by the Helm chart — see [Deployment → Helm Chart → Seeding reference data](../deployment/helm-charts.md#seeding-reference-data) for the defaults, how seeding works, and how to add a strategy in production.

### APIs

Refer [API Reference](api-reference.md).



