# Example Implementation Workflow

This walks through adding a register to the
[pbms-connectors](https://github.com/OpenG2P/pbms-connectors) repo, using a `student` register as the
example. The shipped [`farmer`](https://github.com/OpenG2P/pbms-connectors/blob/develop/extensions/registry-adapters/src/openg2p_bg_task_registry_adapters/computations/farmer.py),
[`household`](https://github.com/OpenG2P/pbms-connectors/blob/develop/extensions/registry-adapters/src/openg2p_bg_task_registry_adapters/computations/household.py)
and [`disability`](https://github.com/OpenG2P/pbms-connectors/blob/develop/extensions/registry-adapters/src/openg2p_bg_task_registry_adapters/computations/disability.py)
registers follow the same pattern.

Paths below are relative to `extensions/registry-adapters/src/openg2p_bg_task_registry_adapters/` unless
they start with `odoo/` or `helm/`.

## 1. Add the register type

Add the value to `G2PRegistryType` in both enums. The values must match.

```python
# models/enum.py, and odoo/g2p_registry_type_addon/models/registry_type.py
class G2PRegistryType(Enum):
    FARMER = "farmer"
    HOUSEHOLD = "household"
    DISABILITY = "disability"
    STUDENT = "student"
```

In the Odoo file also add the model to `G2PTargetModelMapping.MODEL_MAPPING`
(`"student": "g2p.register.students"`). The Odoo side is covered in [Registry Add-ons](../registry-addons/README.md).

## 2. Add the register model and search schema

The SQLAlchemy model describes the register's table or view in the registry database
([Registry Database Contract](../registry-database-contract.md)). The `db` connector selects every
column it declares.

```python
# models/registry_student.py
from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class G2PStudentRegistry(G2PRegistry):
    __tablename__ = "g2p_register_students"

    functional_record_id: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=True)
```

```python
# schema/registry_student.py
from typing import Optional

from .registry import G2PRegistryPayload


class G2PStudentRegistryPayload(G2PRegistryPayload):
    functional_record_id: Optional[str] = None
    first_name: Optional[str] = None
    gender: Optional[str] = None
    grade: Optional[int] = None
```

Export both from `models/__init__.py` and `schema/__init__.py`.

## 3. Add the summary model, schema and computation

Each register stores its own summary statistics. Extend the base summary model and schema:

```python
# models/beneficiary_list_summary_student.py
from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import Float, String
from sqlalchemy.orm import mapped_column


class BeneficiaryListSummaryStudent(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_student"

    grade_mean = mapped_column(Float, default=0)
    grade_units = mapped_column(String, nullable=True)
```

```python
# schema/beneficiary_list_summary_student.py
from typing import Optional

from pydantic import BaseModel

from .beneficiary_list_summary import BeneficiaryListSummaryPayload


class BeneficiaryListSummaryStudent(BaseModel):
    grade_mean: Optional[str] = None


class BeneficiaryListSummaryStudentPayload(BeneficiaryListSummaryPayload):
    registry_summary: BeneficiaryListSummaryStudent
```

Add the summary model to `get_models()` in `migrate.py` so its table is created in the bg-task
database.

Then add a `StudentSummaries` mixin in `computations/_summary.py` with `get_summary`,
`get_summary_sync`, `compute_eligibility_statistics` and `compute_entitlement_statistics`. Read
registrants with `self.fetch_by_ids(ids)`, which works on both connectors, and reuse the helpers there
(`apply_quartiles`, `gendered_entitlement_values`). `FarmerSummaries` is the fullest example.

## 4. Add the DB and DCI classes

One file per register, with two small classes on the shared base classes
([Key Components](key-components.md)):

```python
# computations/student.py
from ..dci import identifier_value
from ..models import G2PStudentRegistry
from ..schema import G2PStudentRegistryPayload
from ._base import RegistryDB, RegistryDCI
from ._dci_records import as_int, code, text
from ._summary import StudentSummaries


class StudentDB(StudentSummaries, RegistryDB):
    model = G2PStudentRegistry
    payload = G2PStudentRegistryPayload


class StudentDCI(StudentSummaries, RegistryDCI):
    payload = G2PStudentRegistryPayload
    reg_type = "Student"
    reg_record_type = "Student"
    match_field = "functional_record_id"
    fields = {"functional_record_id", "first_name", "gender", "grade"}

    @staticmethod
    def flat(record: dict) -> dict:
        demographic = record.get("demographic_info") or {}
        name = demographic.get("name") or {}
        return {
            "functional_record_id": identifier_value(record, ("member_identifier",)),
            "first_name": text(name.get("given_name")),
            "gender": code(demographic.get("sex")),
            "grade": as_int(record.get("grade")),
        }
```

`flat()` maps the registry's DCI record (as rendered by its outgoing template) onto the same column
names as the DB model, so the same eligibility domains work on both connectors. Export both classes
from `computations/__init__.py`.

## 5. Register it

Add the pair to `registers.py`. The factory needs no change.

```python
# registers.py
REGISTERS = {
    G2PRegistryType.FARMER.value: (FarmerDB, FarmerDCI),
    G2PRegistryType.HOUSEHOLD.value: (HouseholdDB, HouseholdDCI),
    G2PRegistryType.DISABILITY.value: (DisabilityDB, DisabilityDCI),
    G2PRegistryType.STUDENT.value: (StudentDB, StudentDCI),
}
```

## 6. Add the chart settings

In `helm/openg2p-pbms/values.yaml`, add the register's defaults and its two environment variables to
the shared `registryAdapterEnv` block (used by the Celery workers and the staff portal API):

```yaml
global:
  registers:
    student:
      connector: db
      connectionString: 'postgresql://registry_user:CHANGE_ME@{{ .Values.global.postgresqlHost }}:5432/registry'

# in the registryAdapterEnv block
REGISTRY_ADAPTERS_STUDENT_CONNECTOR: '{{ .Values.global.registers.student.connector }}'
REGISTRY_ADAPTERS_STUDENT_CONNECTION_STRING: '{{ tpl .Values.global.registers.student.connectionString $ }}'
```

Then copy a register block in `helm/openg2p-pbms/questions.own.yaml` so Rancher shows a "Student
Register" group.

`test/test_register_config.py` fails CI if the two enums, `registers.py`, `values.yaml` and
`questions.own.yaml` disagree.

## 7. Build and deploy

Merging to `develop` builds and publishes the `openg2p-pbms-odoo`, `openg2p-pbms-celery` and
`openg2p-pbms-staff-api` images and the `openg2p-pbms` chart as `0.0.0-develop.<n>`. Install it with the
register's connector and connection string set (see [Configuration](README.md#configuration)).
