# Игра "Пакман"

## Запуск
Запуск файла main.py (должна быть установлена библиотека pygame).

## Описание игры
Упрощённый клон известной игры.

Игрок управляет персонажем, основная цель - собрать все очки и не быть пойманным призраками.

Игрок выигрывает, если собирает все очки. Собранные очки отображаются в левом верхнем углу экрана.


## Структура проекта:
* data - папка с данными
  * images - папка с изображениями
  * level* - файлы с картами уровней (см. раздел "Описание карты уровня")
* main.py - файл с программой
* readme.md - описание проекта (этот файл)
* requirements.txt - описание зависимостей для сборки и запуска проекта

## Описание карты уровня
Текстовый файл без расширения.

Для использования в игре положите его в папку data и добавьте его имя к списку LEVELS в начале программы.

В случае, если не отмечены место старта игрока или призраков, места для игрока и/или призраков будут определяться случайно.

В таких случаях возможны неудачные старты — призраки могут оказаться достаточно близко или заблокировать все проходы.

### Условные обозначения

|Символ|Значение|
|---|---|
| \# | стена |
| . | обычная клетка, очко для сбора персонажем |
| @ | место старта игрока, если не указано, игрок появляется в случайной обычной клетке |
| <пробел> | свободное место, в том числе за пределами стен |
| ! | место старта призрака, если не указано, призрак появится на случайной обычной клетке |
