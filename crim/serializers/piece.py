from crim.models.document import CRIMSource
from crim.models.genre import CRIMGenre
from crim.models.mass import CRIMMass
from crim.models.observation import CRIMObservation
from crim.models.part import CRIMPart
from crim.models.person import CRIMPerson
from crim.models.phrase import CRIMPhrase
from crim.models.piece import CRIMPiece
from crim.models.relationship import CRIMRelationship
from crim.models.role import CRIMRoleType, CRIMRole
from crim.models.voice import CRIMVoice
from rest_framework import serializers


class CRIMRoleTypePieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimroletype-detail-data', lookup_field='role_type_id')

    class Meta:
        model = CRIMRoleType
        fields = (
            'url',
            'role_type_id',
            'name',
        )


class CRIMGenrePieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimgenre-detail-data', lookup_field='genre_id')

    class Meta:
        model = CRIMGenre
        fields = (
            'url',
            'name',
        )


class CRIMPersonPieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimperson-detail-data', lookup_field='person_id')

    class Meta:
        model = CRIMPerson
        fields = (
            'url',
            'name',
        )


class CRIMRolePieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimrole-detail-data', lookup_field='id')
    person = CRIMPersonPieceSerializer(read_only=True)
    role_type = CRIMRoleTypePieceSerializer(read_only=True)

    class Meta:
        model = CRIMRole
        fields = (
            'url',
            'person',
            'role_type',
            'date',
            'remarks',
        )


class CRIMMassMovementPieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='crimpiece-detail-data',
        lookup_field='piece_id',
    )
    pdf_links = serializers.SerializerMethodField()
    mei_links = serializers.SerializerMethodField()

    class Meta:
        model = CRIMPiece
        fields = (
            'url',
            'piece_id',
            'title',
            'pdf_links',
            'mei_links',
        )

    def get_pdf_links(self, obj):
        return obj.pdf_links.split('\n')

    def get_mei_links(self, obj):
        return obj.mei_links.split('\n')


class CRIMMassPieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='crimmass-detail-data',
        lookup_field='mass_id',
    )
    roles = CRIMRolePieceSerializer(
        many=True,
        read_only=True,
        source='roles_as_mass',
    )
    movements = CRIMMassMovementPieceSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = CRIMMass
        fields = (
            'url',
            'mass_id',
            'title',
            'roles',
            'movements',
        )


class CRIMSourcePieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='crimsource-detail-data',
        lookup_field='document_id',
    )
    roles = CRIMRolePieceSerializer(
        many=True,
        read_only=True,
        source='roles_as_source',
    )
    external_links = serializers.SerializerMethodField()

    class Meta:
        model = CRIMSource
        fields = (
            'url',
            'document_id',
            'title',
            'roles',
            'external_links',
        )

    def get_external_links(self, obj):
        return obj.external_links.split('\n')


class CRIMPieceSummarySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimpiece-detail-data', lookup_field='piece_id')
    mass = CRIMMassPieceSerializer(read_only=True)

    class Meta:
        model = CRIMPiece
        fields = (
            'url',
            'piece_id',
            'title',
            'mass',
        )


class CRIMObservationPieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='crimobservation-detail-data',
        lookup_field='id',
    )
    observer = CRIMPersonPieceSerializer(read_only=True)
    piece = CRIMPieceSummarySerializer(read_only=True)

    class Meta:
        model = CRIMObservation
        fields = (
            'url',
            'id',
            'observer',
            'piece',
            'ema',
            'musical_type',
            'mt_cf',
            'mt_cf_voices',
            'mt_cf_dur',
            'mt_cf_mel',
            'mt_sog',
            'mt_sog_voices',
            'mt_sog_dur',
            'mt_sog_mel',
            'mt_sog_ostinato',
            'mt_sog_periodic',
            'mt_csog',
            'mt_csog_voices',
            'mt_csog_dur',
            'mt_csog_mel',
            'mt_cd',
            'mt_cd_voices',
            'mt_fg',
            'mt_fg_voices',
            'mt_fg_int',
            'mt_fg_tint',
            'mt_fg_periodic',
            'mt_fg_strict',
            'mt_fg_flexed',
            'mt_fg_sequential',
            'mt_fg_inverted',
            'mt_fg_retrograde',
            'mt_pe',
            'mt_pe_voices',
            'mt_pe_int',
            'mt_pe_tint',
            'mt_pe_strict',
            'mt_pe_flexed',
            'mt_pe_flt',
            'mt_pe_sequential',
            'mt_pe_added',
            'mt_pe_invertible',
            'mt_id',
            'mt_id_voices',
            'mt_id_int',
            'mt_id_tint',
            'mt_id_strict',
            'mt_id_flexed',
            'mt_id_flt',
            'mt_id_invertible',
            'mt_nid',
            'mt_nid_voices',
            'mt_nid_int',
            'mt_nid_tint',
            'mt_nid_strict',
            'mt_nid_flexed',
            'mt_nid_flt',
            'mt_nid_sequential',
            'mt_nid_invertible',
            'mt_hr',
            'mt_hr_voices',
            'mt_hr_simple',
            'mt_hr_staggered',
            'mt_hr_sequential',
            'mt_hr_fauxbourdon',
            'mt_cad',
            'mt_cad_cantizans',
            'mt_cad_tenorizans',
            'mt_cad_type',
            'mt_cad_tone',
            'mt_cad_dtv',
            'mt_cad_dti',
            'mt_int',
            'mt_int_voices',
            'mt_int_p6',
            'mt_int_p3',
            'mt_int_c35',
            'mt_int_c83',
            'mt_int_c65',
            'mt_fp',
            'mt_fp_ir',
            'mt_fp_range',
            'mt_fp_comment',
            'remarks',
            'created',
            'updated',
        )


class CRIMRelationshipPieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimrelationship-detail-data', lookup_field='id')
    observer = CRIMPersonPieceSerializer(read_only=True)
    model_observation = CRIMObservationPieceSerializer(read_only=True)
    derivative_observation = CRIMObservationPieceSerializer(read_only=True)

    class Meta:
        model = CRIMRelationship
        fields = (
            'url',
            'id',
            'observer',
            'model_observation',
            'derivative_observation',
            'relationship_type',
            'musical_type',
            'rt_q',
            'rt_q_x',
            'rt_q_monnayage',
            'rt_tm',
            'rt_tm_snd',
            'rt_tm_minv',
            'rt_tm_retrograde',
            'rt_tm_ms',
            'rt_tm_transposed',
            'rt_tm_invertible',
            'rt_tnm',
            'rt_tnm_embellished',
            'rt_tnm_reduced',
            'rt_tnm_amplified',
            'rt_tnm_truncated',
            'rt_tnm_ncs',
            'rt_tnm_ocs',
            'rt_tnm_ocst',
            'rt_tnm_nc',
            'rt_nm',
            'rt_om',
            'remarks',
            'created',
            'updated',
        )


class CRIMPartPieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimpart-detail-data', lookup_field='part_id')

    class Meta:
        model = CRIMPart
        fields = (
            'url',
            'name',
            'order',
        )


class CRIMPhrasePieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimphrase-detail-data', lookup_field='phrase_id')
    part = CRIMPartPieceSerializer(read_only=True)

    class Meta:
        model = CRIMPhrase
        fields = (
            'url',
            'part',
            'number',
            'start_measure',
            'stop_measure',
            'text',
        )


class CRIMVoicePieceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimvoice-detail-data', lookup_field='voice_id')

    class Meta:
        model = CRIMVoice
        fields = (
            'url',
            'order',
            'original_name',
            'regularized_name',
            'clef',
        )


class CRIMPieceListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimpiece-detail-data', lookup_field='piece_id')
    voices = CRIMVoicePieceSerializer(
        many=True,
        read_only=True,
    )
    roles = CRIMRolePieceSerializer(
        many=True,
        read_only=True,
        source='roles_as_piece',
    )
    mass = CRIMMassPieceSerializer(read_only=True)
    genre = CRIMGenrePieceSerializer(read_only=True)
    pdf_links = serializers.SerializerMethodField()
    mei_links = serializers.SerializerMethodField()

    class Meta:
        model = CRIMPiece
        fields = (
            'url',
            'piece_id',
            'title',
            'genre',
            'mass',
            'voices',
            'roles',
            'pdf_links',
            'mei_links',
            'remarks',
        )

    def get_pdf_links(self, obj):
        return obj.pdf_links.split('\n')

    def get_mei_links(self, obj):
        return obj.mei_links.split('\n')


class CRIMPieceDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimpiece-detail-data', lookup_field='piece_id')
    roles = CRIMRolePieceSerializer(
        many=True,
        read_only=True,
        source='roles_as_piece',
    )
    mass = CRIMMassPieceSerializer(read_only=True)
    genre = CRIMGenrePieceSerializer(read_only=True)
    phrases = CRIMPhrasePieceSerializer(
        read_only=True,
        many=True,
    )
    voices = CRIMVoicePieceSerializer(
        many=True,
        read_only=True,
    )
    sources = CRIMSourcePieceSerializer(
        many=True,
        read_only=True,
    )
    models = CRIMPieceSummarySerializer(
        many=True,
        read_only=True
    )
    derivatives = CRIMPieceSummarySerializer(
        many=True,
        read_only=True
    )
    pdf_links = serializers.SerializerMethodField()
    mei_links = serializers.SerializerMethodField()

    class Meta:
        model = CRIMPiece
        fields = (
            'url',
            'piece_id',
            'title',
            'genre',
            'mass',
            'phrases',
            'voices',
            'roles',
            'sources',
            'models',
            'derivatives',
            'pdf_links',
            'mei_links',
            'remarks',
        )

    def get_pdf_links(self, obj):
        return obj.pdf_links.split('\n')

    def get_mei_links(self, obj):
        return obj.mei_links.split('\n')


class CRIMPieceWithObservationsSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimpiece-detail-data', lookup_field='piece_id')
    roles = CRIMRolePieceSerializer(
        many=True,
        read_only=True,
        source='roles_as_piece',
    )
    mass = CRIMMassPieceSerializer(read_only=True)
    genre = CRIMGenrePieceSerializer(read_only=True)
    phrases = CRIMPhrasePieceSerializer(
        read_only=True,
        many=True,
    )
    sources = CRIMSourcePieceSerializer(
        many=True,
        read_only=True,
    )
    observations = CRIMObservationPieceSerializer(
        many=True,
        read_only=True,
    )
    pdf_links = serializers.SerializerMethodField()
    mei_links = serializers.SerializerMethodField()

    class Meta:
        model = CRIMPiece
        fields = (
            'url',
            'piece_id',
            'title',
            'genre',
            'mass',
            'phrases',
            'roles',
            'sources',
            'observations',
            'pdf_links',
            'mei_links',
            'remarks',
        )

    def get_pdf_links(self, obj):
        return obj.pdf_links.split('\n')

    def get_mei_links(self, obj):
        return obj.mei_links.split('\n')


class CRIMPieceWithRelationshipsSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='crimpiece-detail-data', lookup_field='piece_id')
    roles = CRIMRolePieceSerializer(
        many=True,
        read_only=True,
        source='roles_as_piece',
    )
    mass = CRIMMassPieceSerializer(read_only=True)
    genre = CRIMGenrePieceSerializer(read_only=True)
    phrases = CRIMPhrasePieceSerializer(
        read_only=True,
        many=True,
    )
    sources = CRIMSourcePieceSerializer(
        many=True,
        read_only=True,
    )
    relationships_as_model = CRIMRelationshipPieceSerializer(
        many=True,
        read_only=True,
    )
    relationships_as_derivative = CRIMRelationshipPieceSerializer(
        many=True,
        read_only=True,
    )
    pdf_links = serializers.SerializerMethodField()
    mei_links = serializers.SerializerMethodField()

    class Meta:
        model = CRIMPiece
        fields = (
            'url',
            'piece_id',
            'title',
            'genre',
            'mass',
            'phrases',
            'roles',
            'sources',
            'relationships_as_model',
            'relationships_as_derivative',
            'pdf_links',
            'mei_links',
            'remarks',
        )

    def get_pdf_links(self, obj):
        return obj.pdf_links.split('\n')

    def get_mei_links(self, obj):
        return obj.mei_links.split('\n')
