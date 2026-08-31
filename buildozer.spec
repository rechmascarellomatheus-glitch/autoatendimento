[app]
title = Autoatendimento
package.name = autoatendimento
package.domain = org.caixa

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg

version = 1.0

requirements = python3,kivy

orientation = portrait

fullscreen = 0

# O banco SQLite é criado automaticamente no diretório privado do app.
# Não é necessário incluir caixa.db no APK.

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
