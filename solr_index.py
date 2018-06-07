import os
import sys
import solr
import uuid


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crim.settings")
    # List all models that will be indexed here
    from crim.models.relationship import CRIMRelationship
    from django.conf import settings

    print('Using: {0}'.format(settings.SOLR_SERVER))
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)

    relationships = CRIMRelationship.objects.all()
    for i, relationship in enumerate(relationships):
        model_piece = relationship.model_observation.piece

        # composer, etc...

        # Example of copying data from object:
        # if relationship.status:
        #     status = True

        d = {
            'type': 'crim_relationship',
            # 'id': str(uuid.uuid4()),
            # 'analysis_id': analysis.id,
            # ...
        }
        # print d
        solrconn.add(**d)
        if i % 100 == 0:
            solrconn.commit()
    solrconn.commit()
    print('Done adding relationships')

    sys.exit()
