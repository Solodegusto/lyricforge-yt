import streamlit as st
from src.audio import AudioDownloadError, cleanup_file, download_audio_temp
from src.formatters import (
    sanitize_filename,
    to_bilingual_srt,
    to_bilingual_txt,
    to_lrc,
    to_srt,
    to_txt,
)
from src.i18n import TARGET_TRANSLATION_NAMES, UI_TEXTS
from src.transcriber import TranscriptionError, transcribe_audio
from src.translator import TranslationError, translate_segments

st.set_page_config(
    page_title="LyricForge YT",
    page_icon="🎵",
    layout="wide",
)


def main() -> None:
    if "ui_lang" not in st.session_state:
        st.session_state["ui_lang"] = "tr"

    with st.sidebar:
        ui_lang = st.selectbox(
            UI_TEXTS[st.session_state["ui_lang"]]["ui_lang_label"],
            options=["tr", "en", "es"],
            format_func=lambda code: {"tr": "🇹🇷 Türkçe", "en": "🇬🇧 English", "es": "🇪🇸 Español"}[code],
            index=["tr", "en", "es"].index(st.session_state["ui_lang"]),
        )
        st.session_state["ui_lang"] = ui_lang
        t = UI_TEXTS[ui_lang]

        st.divider()
        st.header(t["sidebar_header"])

        hw_keys = list(t["hw_options"].keys())
        hardware_mode = st.selectbox(
            t["hw_label"],
            options=hw_keys,
            format_func=lambda k: t["hw_options"][k],
            index=0,
            help=t["hw_help"],
        )

        model_size = st.selectbox(
            t["model_label"],
            options=["tiny", "base", "small", "medium", "large-v3"],
            index=2,
            help=t["model_help"],
        )

        src_lang_keys = list(t["src_lang_options"].keys())
        selected_src_key = st.selectbox(
            t["src_lang_label"],
            options=src_lang_keys,
            format_func=lambda k: t["src_lang_options"][k],
            index=0,
        )
        selected_language = None if selected_src_key == "auto" else selected_src_key

        st.divider()
        st.info(t["privacy_note"])

    t = UI_TEXTS[st.session_state["ui_lang"]]

    st.title(t["title"])
    st.caption(t["subtitle"])

    url = st.text_input(
        t["url_label"],
        placeholder=t["url_placeholder"],
    )

    extract_clicked = st.button(t["extract_btn"], type="primary", use_container_width=True)

    if extract_clicked:
        audio_path = ""
        try:
            with st.status(t["status_running"], expanded=True) as status:
                st.write(t["step_download"])
                audio_path, video_title = download_audio_temp(url)

                st.write(t["step_transcribe"])
                result = transcribe_audio(
                    audio_path=audio_path,
                    model_size=model_size,
                    hardware_mode=hardware_mode,
                    language=selected_language,
                )

                status.update(label=t["status_done"], state="complete", expanded=False)

            st.session_state["lyric_result"] = {
                "title": video_title,
                "language": result.language,
                "prob": result.language_probability,
                "device": result.device_used,
                "compute_type": result.compute_type_used,
                "segments": result.segments,
                "translations": {},
            }

        except AudioDownloadError as err:
            msg = t["err_url_empty"] if str(err) == "URL_EMPTY" else str(err)
            st.error(f"❌ {msg}")
        except TranscriptionError as err:
            if str(err) == "NO_CUDA":
                msg = t["err_no_cuda"]
            elif str(err) == "NO_VOCALS":
                msg = t["err_no_vocals"]
            else:
                msg = str(err)
            st.error(f"❌ {msg}")
        except Exception as err:
            st.error(f"❌ {err}")
        finally:
            if audio_path:
                cleanup_file(audio_path)

    if "lyric_result" in st.session_state:
        data = st.session_state["lyric_result"]
        safe_name = sanitize_filename(data["title"])
        orig_segments = data["segments"]

        st.subheader(f"🎤 {data['title']}")

        col1, col2, col3 = st.columns(3)
        col1.metric(t["metric_lang"], f"{data['language'].upper()} (%{data['prob']*100:.1f})")
        col2.metric(t["metric_device"], data["device"].upper())
        col3.metric(t["metric_compute"], data["compute_type"])

        st.markdown(f"### {t['lyrics_header']}")

        tr_col1, tr_col2 = st.columns([3, 1])
        with tr_col1:
            default_target = st.session_state["ui_lang"]
            target_options = ["tr", "en", "es"]
            target_lang = st.selectbox(
                t["translate_target_label"],
                options=target_options,
                format_func=lambda code: TARGET_TRANSLATION_NAMES[code],
                index=target_options.index(default_target),
            )
        with tr_col2:
            st.write("")
            st.write("")
            translate_clicked = st.button(f"🌍 {t['translate_btn']}", use_container_width=True)

        if translate_clicked and target_lang not in data["translations"]:
            try:
                with st.spinner(t["translating_spinner"]):
                    translated_segs = translate_segments(orig_segments, target_lang=target_lang)
                    data["translations"][target_lang] = translated_segs
            except TranslationError as err:
                st.error(f"❌ {err}")

        has_translation = target_lang in data["translations"]
        trans_segments = data["translations"].get(target_lang)

        tab1, tab2, tab3 = st.tabs([t["tab_original"], t["tab_translate"], t["tab_bilingual"]])

        orig_txt = to_txt(orig_segments)
        with tab1:
            st.text_area(
                label="Original Lyrics",
                value=orig_txt,
                height=340,
                label_visibility="collapsed",
            )

        with tab2:
            if has_translation and trans_segments:
                st.text_area(
                    label="Translated Lyrics",
                    value=to_txt(trans_segments),
                    height=340,
                    label_visibility="collapsed",
                )
            else:
                st.info(f"👆 {t['translate_target_label']} → **{t['translate_btn']}**")

        with tab3:
            if has_translation and trans_segments:
                st.text_area(
                    label="Bilingual Lyrics",
                    value=to_bilingual_txt(orig_segments, trans_segments),
                    height=340,
                    label_visibility="collapsed",
                )
            else:
                st.info(f"👆 {t['translate_target_label']} → **{t['translate_btn']}**")

        st.markdown(f"### {t['download_header']}")
        st.caption(t["dl_orig_section"])
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                label=t["dl_txt"],
                data=orig_txt.encode("utf-8"),
                file_name=f"{safe_name}.txt",
                mime="text/plain; charset=utf-8",
                use_container_width=True,
            )
        with d2:
            st.download_button(
                label=t["dl_srt"],
                data=to_srt(orig_segments).encode("utf-8"),
                file_name=f"{safe_name}.srt",
                mime="application/x-subrip; charset=utf-8",
                use_container_width=True,
            )
        with d3:
            st.download_button(
                label=t["dl_lrc"],
                data=to_lrc(orig_segments, title=data["title"]).encode("utf-8"),
                file_name=f"{safe_name}.lrc",
                mime="text/plain; charset=utf-8",
                use_container_width=True,
            )

        if has_translation and trans_segments:
            st.caption(f"{t['dl_trans_section']} ({target_lang.upper()})")
            td1, td2, td3 = st.columns(3)
            with td1:
                st.download_button(
                    label=f"{t['dl_txt']} [{target_lang.upper()}]",
                    data=to_txt(trans_segments).encode("utf-8"),
                    file_name=f"{safe_name}_{target_lang}.txt",
                    mime="text/plain; charset=utf-8",
                    use_container_width=True,
                )
            with td2:
                st.download_button(
                    label=f"{t['dl_srt']} [{target_lang.upper()}]",
                    data=to_srt(trans_segments).encode("utf-8"),
                    file_name=f"{safe_name}_{target_lang}.srt",
                    mime="application/x-subrip; charset=utf-8",
                    use_container_width=True,
                )
            with td3:
                st.download_button(
                    label=f"{t['dl_lrc']} [{target_lang.upper()}]",
                    data=to_lrc(trans_segments, title=f"{data['title']} ({target_lang.upper()})").encode("utf-8"),
                    file_name=f"{safe_name}_{target_lang}.lrc",
                    mime="text/plain; charset=utf-8",
                    use_container_width=True,
                )

            st.caption(f"{t['dl_bi_section']} (ORIG + {target_lang.upper()})")
            bd1, bd2 = st.columns(2)
            with bd1:
                st.download_button(
                    label=f"{t['dl_txt']} [ORIG+{target_lang.upper()}]",
                    data=to_bilingual_txt(orig_segments, trans_segments).encode("utf-8"),
                    file_name=f"{safe_name}_bilingual_{target_lang}.txt",
                    mime="text/plain; charset=utf-8",
                    use_container_width=True,
                )
            with bd2:
                st.download_button(
                    label=f"{t['dl_srt']} [ORIG+{target_lang.upper()}]",
                    data=to_bilingual_srt(orig_segments, trans_segments).encode("utf-8"),
                    file_name=f"{safe_name}_bilingual_{target_lang}.srt",
                    mime="application/x-subrip; charset=utf-8",
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
