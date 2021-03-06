from django.db import models
from django.utils.text import slugify


class CRIMGenre(models.Model):
    class Meta:
        app_label = 'crim'
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    genre_id = models.SlugField(
        max_length=32,
        unique=True,
        db_index=True,
    )
    name = models.CharField(max_length=32)
    name_plural = models.CharField(max_length=32, blank=True)
    remarks = models.TextField('remarks (supports Markdown)', blank=True)

    def __str__(self):
        return '{0}'.format(self.name)

    def _get_unique_slug(self):
        slug_base = slugify(self.name)
        unique_slug = slug_base
        num = 1
        while CRIMGenre.objects.filter(genre_id=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug_base, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        # Create unique genre_id based on the name
        if not self.genre_id:
            self.genre_id = self._get_unique_slug()
        # Finalize changes
        super().save()
