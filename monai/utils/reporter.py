from humbug.consent import HumbugConsent
from humbug.report import Reporter, Modes

from .module import get_torch_version_tuple

import uuid
from .._version import get_versions

HUMBUG_TOKEN = "48dff1a9-0f64-4f14-848a-0dfde7568e5b"
HUMBUG_KB_ID = "5b637900-c32f-4b41-b949-5ac6e28bde52"
version_dict = get_versions()

session_id = str(uuid.uuid4())
session_id_tag = "session_id:{}".format(session_id)

version_tag = f"{version_dict.get('version', '0+unknown')}-dev-reporting"
revision_tag = version_dict.get("full-revisionid", None)

torch_version = ".".join([str(i) for i in get_torch_version_tuple()])
if not torch_version:
    torch_version = 'unknown'

monai_version_tag = "version:{}".format(version_tag)
monai_revision_tag = "revision:{}".format(revision_tag)
tourch_version_tag = "pytorch:{}".format(torch_version)

monai_tags = [monai_version_tag, monai_revision_tag, tourch_version_tag]

class ConsentState:
    def __init__(self, consent: bool = False) -> None:
        self.consent: bool = consent

    def check(self) -> bool:
        return self.consent

monai_consent_state = ConsentState(False)

monai_consent = HumbugConsent(monai_consent_state.check)
monai_reporter = Reporter(
    name="MONAI",
    consent=monai_consent,
    client_id=None,
    session_id=session_id,
    bugout_token=HUMBUG_TOKEN,
    bugout_journal_id=HUMBUG_KB_ID,
    mode=Modes.DEFAULT
)

def setup_excepthook():
    monai_reporter.system_report(publish=True, tags=monai_tags)
    monai_reporter.setup_excepthook(publish=True, tags=monai_tags)
