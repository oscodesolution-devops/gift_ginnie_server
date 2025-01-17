from django.db import models


class ProductRating(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField()
    review = models.TextField(blank=True, null=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Rating"
        verbose_name_plural = "Product Ratings"
        unique_together = ('product','user')

    def __str__(self):
        return self.product.name + " - " + str(self.rating)
