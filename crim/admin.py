from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms

from crim.models.userprofile import CRIMUserProfile
from crim.models.person import CRIMPerson

from crim.models.document import CRIMDocument, CRIMTreatise, CRIMSource
from crim.models.piece import CRIMGenre, CRIMPiece, CRIMMassMovement
from crim.models.mass import CRIMMass
from crim.models.role import CRIMRole, CRIMRoleType
from crim.models.relationship import CRIMRelationshipType, CRIMMusicalType, CRIMRelationship

from crim.models.note import CRIMNote
from crim.models.comment import CRIMComment
from crim.models.discussion import CRIMDiscussion


class CRIMRolePieceInline(admin.TabularInline):
    model = CRIMRole
    exclude = ['mass', 'treatise', 'source']
    extra = 1


class CRIMRoleMassInline(admin.TabularInline):
    model = CRIMRole
    exclude = ['piece', 'treatise', 'source']
    extra = 1


class CRIMRoleTreatiseInline(admin.TabularInline):
    model = CRIMRole
    exclude = ['piece', 'mass', 'source']
    extra = 1


class CRIMRoleSourceInline(admin.TabularInline):
    model = CRIMRole
    exclude = ['piece', 'mass', 'treatise']
    extra = 1


class CRIMPieceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genre'].queryset = CRIMGenre.objects.exclude(genre_id='mass')


class CRIMMassMovementForm(forms.ModelForm):
    KYRIE = 'K'
    GLORIA = 'G'
    CREDO = 'C'
    SANCTUS = 'S'
    AGNUS = 'A'
    MASS_MOVEMENTS = [
        (KYRIE, 'Kyrie'),
        (GLORIA, 'Gloria'),
        (CREDO, 'Credo'),
        (SANCTUS, 'Sanctus'),
        (AGNUS, 'Agnus Dei'),
    ]
    title = forms.CharField(widget=forms.Select(choices=MASS_MOVEMENTS))


class CRIMPersonAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(CRIMPersonAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'name_alternate_list':
            formfield.widget = forms.Textarea(attrs={'rows': 3, 'cols': 32})
        return formfield

    fields = [
        'name',
        'name_sort',
        'name_alternate_list',
        'birth_date',
        'death_date',
        'active_date',
        'remarks',
    ]
    list_display = (
        'sorted_name',
        'sorted_date',
    )
    list_filter = [
        'date_sort',
    ]
    search_fields = [
        'name',
        'name_alternate_list',
        'remarks',
    ]
    ordering = ['name_sort', 'date_sort']


class CRIMPieceAdmin(admin.ModelAdmin):
    form = CRIMPieceForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(genre__genre_id='mass')

    fields = [
        'piece_id',
        'title',
        'genre',
        'pdf_link',
        'mei_link',
    ]
    inlines = (CRIMRolePieceInline,)
    search_fields = (
        'piece_id',
        'title',
    )
    list_display = (
        'piece_id',
        'title',
        'genre',
        'sorted_date',
    )
    list_filter = [
        'genre',
    ]
    ordering = ['piece_id']


class CRIMMassMovementAdmin(admin.ModelAdmin):
    form = CRIMMassMovementForm
    fields = [
        'piece_id',
        'mass',
        'title',
        'pdf_link',
        'mei_link',
    ]
    search_fields = (
        'piece_id',
        'mass__title',
        'title',
    )
    list_display = (
        'piece_id',
        'mass',
        'title',
    )
    ordering = ['piece_id']


class CRIMGenreAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'remarks',
    ]
    list_display = (
        'name',
    )


class CRIMRoleAdmin(admin.ModelAdmin):
    search_fields = (
        'person__name',
        'piece__title',
        'mass_movement__mass__title',
        'mass__title',
        'treatise__title',
        'source__title',
    )


class CRIMRoleTypeAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'remarks',
    ]

    list_display = (
        'name',
    )


class CRIMRelationshipTypeAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'remarks',
    ]

    list_display = (
        'name',
    )


class CRIMMusicalTypeAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'remarks',
    ]

    list_display = (
        'name',
    )


class UserProfileInline(admin.StackedInline):
    model = CRIMUserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    ordering = ['username',]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(CRIMPerson, CRIMPersonAdmin)

admin.site.register(CRIMMass)
admin.site.register(CRIMMassMovement, CRIMMassMovementAdmin)
admin.site.register(CRIMPiece, CRIMPieceAdmin)

admin.site.register(CRIMTreatise)
admin.site.register(CRIMSource)

admin.site.register(CRIMRole, CRIMRoleAdmin)
admin.site.register(CRIMRelationship)

admin.site.register(CRIMNote)
admin.site.register(CRIMComment)
admin.site.register(CRIMDiscussion)

admin.site.register(CRIMGenre, CRIMGenreAdmin)
admin.site.register(CRIMRoleType, CRIMRoleTypeAdmin)
admin.site.register(CRIMRelationshipType, CRIMRelationshipTypeAdmin)
admin.site.register(CRIMMusicalType, CRIMMusicalTypeAdmin)
