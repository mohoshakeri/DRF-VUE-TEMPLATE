from django.contrib import admin
from django.contrib.admin.utils import display_for_field as base_display_for_field
from django.db import models
from django.db.models import BooleanField, NullBooleanField
from django.utils.html import format_html
from django_json_widget.widgets import JSONEditorWidget
from jalali_date_new.fields import JalaliDateTimeField, JalaliDateField
from jalali_date_new.widgets import (
    AdminJalaliDateTimeWidget,
    AdminJalaliDateWidget,
)
from massadmin.massadmin import mass_change_selected

from tools.datetimes import jdt


def display_for_field(value, field, *args, **kwargs):
    if isinstance(field, models.DateTimeField) and value:
        return jdt.datetime.fromgregorian(datetime=value).strftime("%Y/%m/%d - %H:%M")
    if isinstance(field, models.DateField) and value:
        return jdt.datetime.fromgregorian(date=value).date().strftime("%Y/%m/%d")
    return base_display_for_field(value, field, *args, **kwargs)


admin.utils.display_for_field = display_for_field


class AbstractAdmin(admin.ModelAdmin):
    model = models.Model
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
        models.DateTimeField: {
            "form_class": JalaliDateTimeField,
            "widget": AdminJalaliDateTimeWidget,
        },
        models.DateField: {
            "form_class": JalaliDateField,
            "widget": AdminJalaliDateWidget,
        },
    }
    list_filter_classes = []
    display_excludes = []
    display_includes = []
    staff_fileds = []
    select_related_fields = []
    prefetch_related_fields = []
    raw_actions = []
    raw_actions_classes = {"delete_selected": "btn-error"}
    exclude_raw_actions = ["mass_change_selected"]
    list_per_page = 100
    free_access = False
    ordering = ("-create", "-update")
    date_hierarchy = "create"

    # 1. QUERYSETS

    def _queryset_handler(self, queryset):
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        return queryset

    def get_queryset(self, request):
        return self._queryset_handler(super().get_queryset(request))

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        queryset = self._queryset_handler(queryset)
        return queryset.distinct(), may_have_duplicates

    # 2. DISPLAYS

    def get_list_display(self, request):
        # Get All Field Names From The Model
        model_fields = [field.name for field in self.model._meta.fields]

        # Get All Property Names That Are Not Methods And Not Private
        property_fields = [
            attr
            for attr in dir(self.model)
            if isinstance(getattr(self.model, attr), property)
            and not attr.startswith("_")
        ]

        # Combine Fields And Properties
        combined_fields = model_fields + property_fields + list(self.display_includes)

        # Now Handle Boolean Properties For Admin Icon
        for prop in property_fields:
            value = getattr(self.model, prop)
            # Only Boolean Properties
            if value.fget and value.fget.__annotations__.get("return") is bool:
                # If Already Exists, No Need To Add Again
                if not hasattr(self.__class__, prop):
                    # Wrap Property To Function And Add Boolean Attribute
                    def wrapper(self, obj, prop=prop):
                        return getattr(obj, prop)

                    wrapper.boolean = True
                    wrapper.short_description = prop.replace("_", " ").title()
                    setattr(self.__class__, prop, wrapper)

        # Exclude The Fields That Are In display_excludes
        fields_display = [
            field for field in combined_fields if field not in self.display_excludes
        ]

        actions = super().get_actions(request)
        self.raw_actions = actions
        fields_display.insert(1, "action_raw_buttons")

        return fields_display

    def action_raw_buttons(self, obj):
        actions = self.raw_actions
        buttons = [
            '<button class="action-btn button btn btn-sm {}" type="button" data-action="{}" data-id="{}">{}</button>'.format(
                self.raw_actions_classes.get(action_name, "btn-primary"),
                action_name,
                obj.id,
                action_name.replace("selected", "").replace("_", " ").title(),
            )
            for action_name in actions.keys()
            if action_name not in self.exclude_raw_actions
        ]

        return format_html(" ".join(buttons))

    action_raw_buttons.short_description = "Actions"

    def get_list_filter(self, request):
        # Start With Defined list_filter If Any
        defined_filters = list(self.list_filter) if hasattr(self, "list_filter") else []

        # Collect Fields Already Included
        defined_filter_names = set()
        for item in defined_filters:
            if isinstance(item, str):
                defined_filter_names.add(item)
            elif hasattr(item, "parameter_name"):
                defined_filter_names.add(item.parameter_name)

        # Get Fields From Model
        model_fields = self.model._meta.fields
        extra_filters = []

        for field in model_fields:
            if field.name in defined_filter_names:
                continue

            # Add Boolean Or NullBoolean Fields
            if isinstance(field, (BooleanField, NullBooleanField)):
                extra_filters.append(field.name)

            # Add Fields With Choices
            elif field.choices:
                extra_filters.append(field.name)

        # Combine And Return
        return defined_filters + extra_filters

    def get_list_display_links(self, request, list_display):
        if request.user.is_superuser:
            return self.list_display_links or ("id",)

        fields = self.get_fields(request)
        if fields:
            return self.list_display_links or ("id",)
        return None

    # 3. FORMS

    def get_fields(self, request, obj=None):
        if self.free_access or request.user.is_superuser:
            fields = super().get_fields(request, obj)
        else:
            fields = self.staff_fileds

        many_to_many_rels = [
            field.name
            for field in self.model._meta.get_fields()
            if field.name in fields
            and isinstance(field, (models.ManyToManyField, models.ManyToManyRel))
        ]
        one_rels = [
            field.name
            for field in self.model._meta.get_fields()
            if field.name in fields
            and isinstance(
                field,
                (
                    models.OneToOneRel,
                    models.ManyToOneRel,
                    models.OneToOneField,
                    models.ForeignKey,
                ),
            )
        ]
        self.raw_id_fields = one_rels
        self.autocomplete_fields = one_rels
        self.filter_horizontal = many_to_many_rels

        return fields

    # 4. ACTIONS
    def get_actions(self, request):
        if self.has_change_permission(request):
            actions = tuple(self.actions or ())
            if mass_change_selected not in actions:
                self.actions = (mass_change_selected,) + actions

        return super().get_actions(request)

    def delete_queryset(self, request, queryset):
        # For distinct bug
        ids = list(queryset.values_list("pk", flat=True))
        clean_queryset = queryset.model.objects.filter(pk__in=ids)
        clean_queryset.delete()
