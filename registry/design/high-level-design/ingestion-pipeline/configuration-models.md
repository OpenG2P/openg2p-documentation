# Configuration models

<mark style="color:blue;">**incoming\_partners**</mark>&#x20;

<table data-header-hidden><thead><tr><th width="312.26800537109375"></th></tr></thead><tbody><tr><td>partner_id</td></tr><tr><td>partner_mnemonic</td></tr><tr><td>keymanager_reference_id</td></tr><tr><td>is_active</td></tr></tbody></table>

<mark style="color:blue;">**subscription\_activity\_log**</mark>

<table data-header-hidden><thead><tr><th width="311.38494873046875"></th></tr></thead><tbody><tr><td><strong>subscription_id</strong></td></tr><tr><td>Is_unsubscribe (bool)</td></tr><tr><td>description</td></tr><tr><td>partner_id</td></tr><tr><td>subscription_url</td></tr><tr><td>header</td></tr><tr><td>payload</td></tr><tr><td>response</td></tr><tr><td>date_time</td></tr></tbody></table>

<mark style="color:blue;">**incoming\_model\_signature\_patterns**</mark>

<table data-header-hidden><thead><tr><th width="310.23663330078125"></th></tr></thead><tbody><tr><td><strong>signature_pattern_id</strong></td></tr><tr><td>data_model_id</td></tr><tr><td>key_path_for_sender</td></tr><tr><td>key_path_for_signature</td></tr><tr><td>key_path_for_signature_payload</td></tr></tbody></table>

<mark style="color:blue;">**incoming\_model\_semantic\_patterns**</mark>

<table data-header-hidden><thead><tr><th width="309.67926025390625"></th></tr></thead><tbody><tr><td><strong>semantic_pattern_id</strong></td></tr><tr><td>data_model_id</td></tr><tr><td>register_id</td></tr><tr><td>operation_id</td></tr><tr><td>pattern_for_register</td></tr><tr><td>patter_for_operation</td></tr><tr><td>key_path_for_business_payload</td></tr></tbody></table>

<mark style="color:blue;">**incoming\_templates**</mark>

<table data-header-hidden><thead><tr><th width="309.38104248046875"></th></tr></thead><tbody><tr><td>template_id</td></tr><tr><td>data_model_id</td></tr><tr><td>register_id</td></tr><tr><td>operation_id</td></tr><tr><td>template_file_id</td></tr></tbody></table>

<mark style="color:blue;">**subscription\_activity\_log**</mark>

<table data-header-hidden><thead><tr><th width="308.6802978515625"></th></tr></thead><tbody><tr><td><strong>subscription_id</strong></td></tr><tr><td>Is_unsubscribe (bool)</td></tr><tr><td>description</td></tr><tr><td>partner_id</td></tr><tr><td>subscription_url</td></tr><tr><td>registry_callback_url</td></tr><tr><td>header</td></tr><tr><td>payload</td></tr><tr><td>response</td></tr><tr><td>date_time</td></tr></tbody></table>

<mark style="color:blue;">**incoming\_payload\_enricher**</mark>

<table data-header-hidden><thead><tr><th width="306.986572265625"></th></tr></thead><tbody><tr><td><strong>enricher_id</strong></td></tr><tr><td>data_model_id</td></tr><tr><td>register_id</td></tr><tr><td>operation_id</td></tr><tr><td>raw_payload_enricher_class</td></tr></tbody></table>

<mark style="color:blue;">**data\_models**</mark>

<table data-header-hidden><thead><tr><th width="303.85443115234375"></th></tr></thead><tbody><tr><td><strong>data_model_id</strong></td></tr><tr><td>data_model_mnemonic</td></tr><tr><td>pattern_for_data_model</td></tr><tr><td>is_active</td></tr></tbody></table>
