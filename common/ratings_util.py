from django.apps import apps


def get_average_rating(recipe_guid):
    Review = apps.get_model('recipedetail', 'Review')
    recipe_reviews = Review.objects.filter(review_recipe_guid=recipe_guid)
    rev_grades = []
    for review in recipe_reviews:
        rev_grades.append(review.review_grade)
    average_rating = 0
    if rev_grades:
        average_rating = sum(rev_grades) / len(rev_grades)
    return average_rating
