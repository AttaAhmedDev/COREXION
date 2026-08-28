"""Reference-counted media cleanup for PageSection images.

Several sections can point at the same uploaded file, so a plain "delete the
file when the row changes" rule would break the remaining sections. Every
deletion here first checks whether any other row still references the file, and
runs on transaction commit so a rolled back save never removes a live file.
"""

import logging

from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import PageSection

logger = logging.getLogger(__name__)

_OLD_IMAGE_ATTR = "_old_image_name"


def _storage():
    return PageSection._meta.get_field("image").storage


def _is_referenced(name, exclude_pk=None):
    queryset = PageSection.objects.filter(image=name)
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)
    return queryset.exists()


def _delete_if_unused(name, exclude_pk=None):
    if not name:
        return

    def run():
        if _is_referenced(name, exclude_pk=exclude_pk):
            logger.debug("Keeping %s, still referenced by another section", name)
            return
        storage = _storage()
        try:
            if storage.exists(name):
                storage.delete(name)
        except Exception:
            logger.exception("Failed to delete unused media file %s", name)

    transaction.on_commit(run)


@receiver(pre_save, sender=PageSection)
def remember_previous_image(sender, instance, raw, **kwargs):
    if raw or not instance.pk:
        setattr(instance, _OLD_IMAGE_ATTR, None)
        return
    previous = (
        sender.objects.filter(pk=instance.pk).values_list("image", flat=True).first()
    )
    setattr(instance, _OLD_IMAGE_ATTR, previous or None)


@receiver(post_save, sender=PageSection)
def delete_replaced_image(sender, instance, raw, created, **kwargs):
    if raw or created:
        return
    old_name = getattr(instance, _OLD_IMAGE_ATTR, None)
    new_name = instance.image.name or None
    if old_name and old_name != new_name:
        _delete_if_unused(old_name)


@receiver(post_delete, sender=PageSection)
def delete_orphaned_image(sender, instance, **kwargs):
    _delete_if_unused(instance.image.name or None)
