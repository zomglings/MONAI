
from humbug.consent import HumbugConsent
from humbug.report import Reporter, Modes, Report

import uuid
from .._version import get_versions

HUMBUG_TOKEN = "e10fbd54-71b0-4e68-80b0-d59ec3d99a81"
HUMBUG_KB_ID = "2e995d6c-95a9-4a35-8ee6-49846ac7fc63"
version_dict = get_versions()

session_id = str(uuid.uuid4())
session_id_tag = "session_id:{}".format(session_id)

version_tag = f"{version_dict.get('version', '0+unknown')}-dev-reporting"
revision_tag = version_dict.get("full-revisionid", None)

monay_version_tag = "version:{}".format(version_tag)
monay_revision_tag = "revision:{}".format(revision_tag)

monay_tags = [monay_version_tag,monay_revision_tag]



def get_reporter(mode=Modes.DEFAULT):
    monay_consent = HumbugConsent(True)
    monay_reporter = Reporter(
        name="MONAI",
        consent=monay_consent,
        client_id=None,
        session_id=session_id,
        bugout_token=HUMBUG_TOKEN,
        bugout_journal_id=HUMBUG_KB_ID,
        mode=mode
    )
    return monay_reporter


def setup_excepthook():
    reporter_obj = get_reporter()
    reporter_obj.system_report(publish=True, tags=monay_tags)
    reporter_obj.setup_excepthook(publish=True, tags=monay_tags)