from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class CRIMRelationship(models.Model):
    class Meta:
        app_label = 'crim'
        verbose_name = 'Relationship'
        verbose_name_plural = 'Relationships'

    observer = models.ForeignKey(
        'CRIMPerson',
        on_delete=models.SET_NULL,
        to_field='person_id',
        null=True,
        db_index=True,
        related_name='relationships',
    )

    model_observation = models.ForeignKey(
        'CRIMObservation',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='observations_as_model',
    )
    derivative_observation = models.ForeignKey(
        'CRIMObservation',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='observations_as_derivative',
    )

    rt_q = models.BooleanField('quotation', default=False)
    rt_q_exact = models.BooleanField('exact', default=False)
    rt_q_monnayage = models.BooleanField('monnayage', default=False)

    rt_tm = models.BooleanField('mechanical transformation', default=False)
    rt_tm_snd = models.BooleanField('sounding in different voice(s)', default=False)
    rt_tm_minv = models.BooleanField('melodically inverted', default=False)
    rt_tm_retrograde = models.BooleanField('retrograde', default=False)
    rt_tm_ms = models.BooleanField('metrically shifted', default=False)
    rt_tm_transposed = models.BooleanField('transposed', default=False)
    rt_tm_invertible = models.BooleanField('double or invertible counterpoint', default=False)

    rt_tnm = models.BooleanField('non-mechanical transformation', default=False)
    rt_tnm_embellished = models.BooleanField('embellished', default=False)
    rt_tnm_reduced = models.BooleanField('reduced', default=False)
    rt_tnm_amplified = models.BooleanField('amplified', default=False)
    rt_tnm_truncated = models.BooleanField('truncated', default=False)
    rt_tnm_ncs = models.BooleanField('new counter-subject', default=False)
    rt_tnm_ocs = models.BooleanField('old counter-subject shifted', default=False)
    rt_tnm_ocst = models.BooleanField('old counter-subject transposed', default=False)
    rt_tnm_nc = models.BooleanField('new combination', default=False)

    rt_nm = models.BooleanField('new material', default=False)
    rt_om = models.BooleanField('omission', default=False)

    remarks = models.TextField('remarks (supports Markdown)', blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField('status', default=True)

    def id_in_brackets(self):
        return '<R' + str(self.id) + '>'
    id_in_brackets.short_description = 'ID'
    id_in_brackets.admin_order_field = 'id'

    def __str__(self):
        return '<R{0}> {1}, {2}'.format(
            self.id,
            self.model_observation.piece_id,
            self.derivative_observation.piece_id
        )

    def save(self, *args, **kwargs):
        # Set the parent relationship type field to true if any of the subtypes are
        if self.rt_q_exact or self.rt_q_monnayage:
            self.rt_q = True
        if (self.rt_tm_snd or self.rt_tm_minv or self.rt_tm_retrograde or
                self.rt_tm_ms or self.rt_tm_transposed or self.rt_tm_invertible):
            self.rt_tm = True
        if (self.rt_tnm_embellished or self.rt_tnm_reduced or self.rt_tnm_amplified or
            self.rt_tnm_truncated or self.rt_tnm_ncs or self.rt_tnm_ocs or
                self.rt_tnm_ocst or self.tnm_nc):
            self.rt_tnm = True
        # Finalize changes
        super().save()


@receiver(post_save, sender=CRIMRelationship)
def solr_index(sender, instance, created, **kwargs):
    print('Indexing in solr')
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query('type:crim_relationship id:{0}'.format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    # use a more specific name
    relationship = instance

    d = {
        'type': 'crim_piece',
        'id': str(uuid.uuid4()),
        'observer': relationship.observer.name,
        'model': relationship.model_observation.piece.title,
        'derivative': relationship.derivative_observation.piece.title,
        'rt_q': relationship.rt_q,
        'rt_q_exact': relationship.rt_q_exact,
        'rt_q_monnayage': relationship.rt_q_monnayage,
        'rt_tm': relationship.rt_tm,
        'rt_tm_snd': relationship.rt_tm_snd,
        'rt_tm_minv': relationship.rt_tm_minv,
        'rt_tm_retrograde': relationship.rt_tm_retrograde,
        'rt_tm_ms': relationship.rt_tm_ms,
        'rt_tm_transposed': relationship.rt_tm_transposed,
        'rt_tm_invertible': relationship.rt_tm_invertible,
        'rt_tnm': relationship.rt_tnm,
        'rt_tnm_embellished': relationship.rt_tnm_embellished,
        'rt_tnm_reduced': relationship.rt_tnm_reduced,
        'rt_tnm_amplified': relationship.rt_tnm_amplified,
        'rt_tnm_truncated': relationship.rt_tnm_truncated,
        'rt_tnm_ncs': relationship.rt_tnm_ncs,
        'rt_tnm_ocs': relationship.rt_tnm_ocs,
        'rt_tnm_ocst': relationship.rt_tnm_ocst,
        'rt_tnm_nc': relationship.rt_tnm_nc,
        'rt_nm': relationship.rt_nm,
        'rt_om': relationship.rt_om,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=CRIMRelationship)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query('type:crim_relationship id:{0}'.format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])
