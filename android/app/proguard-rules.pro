# Android ProGuard rules for LivingAI
# https://developer.android.com/studio/build/shrink-code

# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to the end of the
# flags specified in the common proguard flags file
# (https://developer.android.com/studio/build/shrink-code).
# You can override the common flags in this file.

# For a full list of options, see the ProGuard manual
# (https://www.guardsquare.com/manual/introduction).

# Uncomment this to preserve the line number information for
# debugging stack traces. This will make the APK larger.
#-keepattributes SourceFile,LineNumberTable

# Uncomment this to preserve all classes and members in the main package.
#-keep class com.livingai.app.** { *; }

# Keep all Activities, Services, Receivers, and Providers
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider

# Keep all Parcelable classes
-keep public class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# Keep R classes
-keep class **.R$* {
    *;
}

# Keep all classes in the main package
-keep class com.livingai.app.** { *; }

# Keep all classes in the models package
-keep class com.livingai.app.models.** { *; }

# Keep all classes in the adapters package
-keep class com.livingai.app.adapters.** { *; }

# Keep all classes in the fragments package
-keep class com.livingai.app.fragments.** { *; }

# Keep all classes in the services package
-keep class com.livingai.app.services.** { *; }

# Keep all classes in the receivers package
-keep class com.livingai.app.receivers.** { *; }

# Keep all classes in the utils package
-keep class com.livingai.app.utils.** { *; }

# Keep all classes in the activities package
-keep class com.livingai.app.activities.** { *; }

# Keep ViewModel classes
-keep class * extends androidx.lifecycle.ViewModel { *; }

# Keep Room database classes
-keep class * extends androidx.room.Database { *; }
-keep class * extends androidx.room.Entity { *; }
-keep class * extends androidx.room.Dao { *; }

# Keep Retrofit service interfaces
-keep class * implements retrofit2.http.Service {
    *;
}
-keepattributes Signature
-keepattributes Exceptions
-keepclasseswithmembers class * {
    @retrofit2.* <methods>;
}

# Keep Gson models
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# Keep WorkManager classes
-keep class * extends androidx.work.Worker { *; }

# Keep CameraX classes
-keep class * extends androidx.camera.core.CameraXConfig { *; }

# Keep data binding classes
-keep class * implements android.view.View.OnClickListener { *; }
-keep class * implements android.view.View.OnLongClickListener { *; }

# Keep all WebView and JavaScript interfaces
-keep class * implements android.webkit.JavascriptInterface { *; }

# Keep all native methods
-keepclassmembers class * {
    native <methods>;
}

# Keep all static initializers
-keepclassmembers class * {
    static <clinit>;
}

# Keep all enum values
-keepclassmembers enum * {
    *;
}

# Keep all annotations
-keepattributes *Annotation*

# Keep all inner classes
-keep class *$* {
    *;
}

# Keep all synthetic classes
-keep class * {
    *;
}