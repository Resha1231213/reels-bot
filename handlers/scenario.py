from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from states import ScenarioState
from utils.scenario_utils import extract_topic_from_url, generate_script_with_openai

router = Router()

@router.message(F.text == "🎬 Создать сценарий")
async def ask_script_source(msg: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 Ввести текст"), KeyboardButton(text="🔗 Отправить ссылку")]],
        resize_keyboard=True
    )
    await msg.answer("Как вы хотите задать сценарий?", reply_markup=kb)
    await state.set_state(ScenarioState.select_mode)

@router.message(ScenarioState.select_mode, F.text)
async def handle_mode_choice(msg: Message, state: FSMContext):
    if "текст" in msg.text:
        await msg.answer("✍️ Напишите свой сценарий:")
        await state.set_state(ScenarioState.enter_text)
    elif "ссылк" in msg.text:
        await msg.answer("🔗 Пришлите ссылку на видео (YouTube, TikTok, Instagram):")
        await state.set_state(ScenarioState.enter_url)

@router.message(ScenarioState.enter_text, F.text)
async def handle_custom_script(msg: Message, state: FSMContext):
    await state.update_data(script=msg.text)
    await msg.answer("✅ Сценарий сохранён.")
    await state.clear()

@router.message(ScenarioState.enter_url, F.text)
async def handle_link(msg: Message, state: FSMContext):
    url = msg.text
    await msg.answer("⏳ Извлекаю тему и создаю сценарий...")

    topic = extract_topic_from_url(url)
    if not topic:
        await msg.answer("⚠️ Не удалось извлечь тему из видео. Попробуйте вручную.")
        return

    script = generate_script_with_openai(topic)
    await state.update_data(script=script)
    await msg.answer(f"✅ Сценарий сгенерирован:\n\n{script}")
    await state.clear()
