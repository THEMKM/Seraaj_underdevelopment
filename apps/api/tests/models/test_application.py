from apps.api.models.application import ApplicationCreate, ApplicationStatus


def test_custom_metadata_default():
    app = ApplicationCreate(volunteer_id=1, opportunity_id=1)
    assert app.custom_metadata == {}
    assert app.status == ApplicationStatus.DRAFT
