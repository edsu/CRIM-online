from django.db import models
from django.utils.text import slugify

from crim.models.person import CRIMPerson
from crim.models.mass import CRIMMass

from dateutil.parser import parse


class CRIMGenre(models.Model):
    class Meta:
        app_label = 'crim'
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    genre_id = models.SlugField(
        max_length=32,
        unique=True,
        primary_key=True,
        db_index=True,
    )
    name = models.CharField(max_length=32)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return '{0}'.format(self.name)

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while CRIMGenre.objects.filter(genre_id=unique_slug).exists():
            slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        # Create unique genre_id based on the name
        if not self.genre_id:
            self.genre_id = self._get_unique_slug()
        # Finalize changes
        super().save()



class CRIMPiece(models.Model):
    class Meta:
        app_label = 'crim'
        verbose_name = 'Piece'
        verbose_name_plural = 'Pieces'
    
    piece_id = models.CharField(
        'Piece ID',
        max_length=16,
        unique=True,
        primary_key=True,
        db_index=True,
    )
    roles = models.ManyToManyField(
        CRIMPerson,
        through='CRIMRole',
        through_fields=('piece', 'person'),
    )
    title = models.CharField(max_length=64)
    genre = models.ForeignKey(
        CRIMGenre,
        on_delete=models.SET_NULL,
        to_field='genre_id',
        null=True,
        db_index=True,
    )
    date_of_composition = models.CharField(max_length=32, blank=True, db_index=True)
    date_sort = models.IntegerField(null=True)

#     forces = models.CharField(max_length=16, blank=True)
    pdf_link = models.CharField('PDF link', max_length=255, blank=True)
    mei_link = models.CharField('MEI link', max_length=255, blank=True)
#     audio_link = models.CharField(max_length=255, blank=True)
    
    def sorted_date(self):
        return self.date_sort
    sorted_date.short_description = 'date'
    sorted_date.admin_order_field = 'date_sort'

    def __str__(self):
        roles = self.roles.order_by('date_sort')
        if roles:
            return '[{0}] {1}: {2}'.format(self.piece_id, roles[0], self.title)
        else:
            return '[{0}] {1}'.format(self.piece_id, self.title)

    def _get_date_sort(self):
        try:
            date_parsed = parse(self.date_of_composition, fuzzy=True).year
        except ValueError:
            date_parsed = 0
        return date_parsed

    def save(self, *args, **kwargs):
        # Add sortable date field
        if self._get_date_sort() == 0:
            self.date_sort = None
        else:
            self.date_sort = self._get_date_sort()
        # Finalize changes
        super().save()


class CRIMMassMovement(CRIMPiece):
    class Meta:
        app_label = 'crim'
        verbose_name = 'Mass Movement'
        verbose_name_plural = 'Mass Movements'

    mass = models.ForeignKey(
        CRIMMass,
        on_delete=models.SET_NULL,
        to_field='mass_id',
        null=True,
        db_index=True,
        related_name='movements',
    )

    def save(self):
        self.genre = CRIMGenre(genre_id='mass')
        # TODO: Needs validation that title is one of the following:
        # Kyrie, Gloria, Credo, Sanctus, Agnus Dei
        super().save()
