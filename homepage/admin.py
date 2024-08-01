import datetime
from django.contrib import admin
from .models import Recipe
from login.models import RegisteredUser


class RecipeAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        # Fetch recipe author
        user = obj.recipe_author
        try:
            reg_user = RegisteredUser.objects.get(user=user)
            reg_user.reg_user_warning_count += 1
            # Check whether the user reached the limit of 3 warnings which leads to a temporary ban
            if reg_user.reg_user_warning_count % 3 == 0:
                # Check how many times the user exceeded the warning limit
                warning_overruns = reg_user.reg_user_warning_count / 3
                if warning_overruns >= 5:
                    # If the user exceeded the warning limit 5 times, then ban it permanently (set a suspension end parameter with a lifelong duration)
                    reg_user.reg_user_status["is_suspended"] = True
                    reg_user.reg_user_status["suspension_end"] = format(datetime.date(datetime.MAXYEAR, 12, 31), "%Y-%m-%d")
                    notifications = reg_user.reg_user_status.get("notifications", [])
                    notifications.append(f"Ci dispiace {user.first_name} {user.last_name} ma a causa delle ripetute infrazioni il tuo account è stato permanentemente sospeso da TasteTribe! Non potrai più svolgere alcuna operazione diversa da quelle di guest!")
                    reg_user.reg_user_status["notifications"] = notifications
                else:
                    reg_user.reg_user_status["is_suspended"] = True
                    # Suspend the user for a number of days correspondent to the number of overruns
                    reg_user.reg_user_status["suspension_end"] = format(datetime.datetime.now() + datetime.timedelta(days=warning_overruns), "%Y-%m-%d")
                    notifications = reg_user.reg_user_status.get("notifications", [])
                    notifications.append(f"Ci dispiace {user.first_name} {user.last_name} ma in seguito a ripetuti avvertimenti dobbiamo sospendere il suo account TasteTribe per {warning_overruns} giorni! Potrà continuare ad usare il portale usufruendo delle funzionalità guest")
                    reg_user.reg_user_status["notifications"] = notifications
            else:
                # Send the user a notification containing the warning
                notifications = reg_user.reg_user_status.get("notifications", [])
                notifications.append(f"Gentile {user.first_name} {user.last_name}, la sua ricetta {obj.recipe_name} è stata rimossa poiché considerata non adeguata! La avvisiamo che questo è il suo {reg_user.reg_user_warning_count % 3} avvertimento, al terzo scatterà una sospensione temporanea del suo account TasteTribe")
                reg_user.reg_user_status["notifications"] = notifications
                # Make sure the data regarding the suspension is clean
                reg_user.reg_user_status["is_suspended"] = False
                reg_user.reg_user_status["suspension_end"] = None
            reg_user.save()
        except RegisteredUser.DoesNotExist:
            print("Registered User does not exist, somehow you ended up here")
        # Effectively delete the Recipe
        super().delete_model(request, obj)


# Register your models here.
admin.site.register(Recipe, RecipeAdmin)
