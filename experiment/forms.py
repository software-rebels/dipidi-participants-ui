from django import forms


class TypeAForm(forms.Form):
    deliverable = forms.CharField()


class TypeBForm(forms.Form):
    commit_id = forms.CharField(disabled=True)
    order = forms.IntegerField()


class TypeCForm(forms.Form):
    commit_id = forms.CharField(disabled=True)
    affect = forms.BooleanField(initial=False, required=False)


class TypeC2Form(forms.Form):
    commit_id = forms.CharField(disabled=True)
    configuration = forms.CharField()


class Questionnaire(forms.Form):
    OUR_TOOL_CHOICES = (
        (0, "NA"),
        (1, "Very Useful"),
        (2, "Somehow Useful"),
        (3, "Not Useful")
    )
    FITNESS_CHOICES = (
        (1, "Very Tired"),
        (2, "Tired"),
        (3, "Neutral"),
        (4, "Energetic"),
        (5, "Very Energetic")
    )
    DIFFICULTY_CHOICES = (
        (1, "Easy"),
        (2, "Average"),
        (3, "Hard"),
    )
    PROJECT_EXPERIENCE_CHOICES = (
        (1, "None"),
        (2, "User"),
        (3, "Contributor"),
    )
    other_tools = forms.CharField(label="If you used any other tools (CLI/IDE) please name it here", required=False)
    our_tools = forms.ChoiceField(choices=OUR_TOOL_CHOICES,
                                  label="If we provided a tool for you to use, how useful it was?")

    fitness = forms.ChoiceField(choices=FITNESS_CHOICES,
                                label="How do you feel? (1=Very Tired, 5=Very Energetic)")

    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES,
                                   label="How difficult were the tasks? (1=easy, 2=average, 3=hard)")

    experiment = forms.ChoiceField(choices=PROJECT_EXPERIENCE_CHOICES,
                                   label="How much experience did you have with the projects provided to you?")
    problems = forms.CharField(label="Did you encounter any problem during the experiment?", required=False)
    feedback = forms.CharField(label="Any feedback about the experiment?", required=False)
