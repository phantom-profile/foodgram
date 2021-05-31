from django.contrib import admin

from recipes.models import (Favourite, Follow, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, Tag)


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


class TagInLine(admin.TabularInline):
    model = RecipeTag
    extra = 1


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInLine,
               TagInLine,
               ]
    list_display = ('pk', 'name', 'author', 'pub_date', 'likes')
    list_filter = ('pub_date', 'name', )

    def likes(self, obj):
        return obj.favourite_by.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', )
    list_filter = ('name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user', 'author',)
    list_filter = ('user', 'author',)


class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(Follow)
