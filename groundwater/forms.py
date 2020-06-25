from django import forms


class CsvWellForm(forms.Form):
    """Form to upload CSV file."""

    gw_location_file = forms.FileField(
        label="Choose GW Location excel File:",
        widget=forms.FileInput(),
        required=False
    )

    gw_level_file = forms.FileField(
        label="Choose GW Level excel File:",
        widget=forms.FileInput(),
        required=False
    )
