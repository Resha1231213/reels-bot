from aiogram.fsm.state import State, StatesGroup

class FinalGenerateState(StatesGroup):
    waiting_for_avatar = State()
    waiting_for_voice = State()
    enter_script = State()
    parsed_script = State()
    select_language = State()
    select_format = State()
    with_subtitles = State()


class AvatarGenerationState(StatesGroup):
    uploading_photo = State()
    uploading_video = State()
    confirming_avatar = State()


class VoiceUploadState(StatesGroup):
    recording_voice = State()
    uploading_voice = State()
    confirming_voice = State()


class ScriptCreationState(StatesGroup):
    entering_text_or_link = State()
    confirming_generated_script = State()


class ReelsGenerationState(StatesGroup):
    selecting_avatar = State()
    selecting_voice = State()
    choosing_format = State()
    choosing_subtitles = State()
    confirming_generation = State()


class PackageState(StatesGroup):
    selecting_package = State()
    confirming_payment = State()
    activating_package = State()
