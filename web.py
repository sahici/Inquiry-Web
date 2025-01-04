# Inquiry-Web v1.0
# Signature: Yasin Yaşar

import streamlit as st
from modules.dnsCrawl import DNSChecker
import modules.WPCrawl as WPCrawl
import modules.MoodleCrawl as MoodleCrawl
import modules.subfinder as subfinder
import io
import sys
from typing import Any, Callable

def capture_output(func: Callable, *args: Any) -> str:
    output = io.StringIO()
    sys.stdout = output
    func(*args)
    sys.stdout = sys.__stdout__
    return output.getvalue()

def main() -> None:
    st.set_page_config(
        page_title="Inquiry Web Arayüzü",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 Inquiry Web Arayüzü")
    st.sidebar.header("Tarama Seçenekleri")

    target_url: str = st.text_input("🎯 Hedef URL'yi girin:", key="target_url", on_change=None)

    dns_check: bool = st.sidebar.checkbox("DNS Kayıtları Tara")
    subfinder_check: bool = st.sidebar.checkbox("Subdomain Tara")
    wordpress_check: bool = st.sidebar.checkbox("WordPress Taraması")
    moodle_check: bool = st.sidebar.checkbox("Moodle Taraması")

    if (st.button("🚀 Taramayı Başlat") or target_url) and target_url:
        with st.spinner("⏳ Tarama yapılıyor..."):
            if dns_check:
                with st.expander("🌐 DNS Kayıtları", expanded=True):
                    checker = DNSChecker()
                    results = checker.check_all(target_url)
                    if any(results[record_type] for record_type in ['A', 'CNAME', 'MX', 'NS', 'TXT']):
                        formatted_results = results['domain']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if results['A']:
                                st.markdown("**📍 A Kayıtları:**")
                                for ip in results['A']:
                                    st.code(ip)
                                    cols = st.columns([1, 1, 1, 1])
                                    with cols[0]:
                                        st.link_button("🔍 Censys Bilgileri", f"https://search.censys.io/hosts/{ip}")
                                    with cols[1]:
                                        st.link_button("🔍 Shodan Bilgileri", f"https://www.shodan.io/host/{ip}")
                                    with cols[2]:
                                        st.link_button("🔍 GreyNoise", f"https://viz.greynoise.io/ip/{ip}")
                            
                            if results['CNAME']:
                                st.markdown("**🔄 CNAME Kayıtları:**")
                                for cname in results['CNAME']:
                                    st.code(cname)
                        
                        with col2:
                            if results['MX']:
                                st.markdown("**📧 MX Kayıtları:**")
                                for pref, host in sorted(results['MX']):
                                    st.code(f"{host} (Öncelik: {pref})")
                            
                            if results['NS']:
                                st.markdown("**🌍 NS Kayıtları:**")
                                for ns in results['NS']:
                                    st.code(ns)
                            
                            if results['TXT']:
                                st.markdown("**📝 TXT Kayıtları:**")
                                for txt in results['TXT']:
                                    st.code(txt)
                    else:
                        st.info("DNS kayıtları bulunamadı.")

            if subfinder_check:
                with st.expander("🔍 Subdomain Sonuçları", expanded=True):
                    st.link_button("🔍 CRT.sh Sorgula", f"https://crt.sh/?q={target_url}")
                    subdomain_results = capture_output(subfinder.find_subdomains, target_url)
                    if "Subdomain:" in subdomain_results:
                        subdomains = subdomain_results.split('\n')
                        for line in subdomains:
                            if "Subdomain:" in line:
                                st.markdown(f"**{line}**")
                            elif "Status Code:" in line:
                                st.code(line)
                    else:
                        st.info("Subdomain bulunamadı.")


            if wordpress_check:
                with st.expander("📦 WordPress Tarama Sonuçları", expanded=True):
                    wp_results = capture_output(WPCrawl.run_wordpress_crawl, [target_url])
                    if "WordPress Users:" in wp_results or "Plugin Information:" in wp_results:
                        if "WordPress Users:" in wp_results:
                            st.markdown("**👤 WordPress Kullanıcıları**")
                            users_section = wp_results.split("WordPress Users:")[1].split("Plugin Information:")[0]
                            for line in users_section.strip().split('\n'):
                                if line.strip():
                                    st.code(line.strip())

                        if "Plugin Information:" in wp_results:
                            st.markdown("**🔌 Eklenti Bilgileri**")
                            plugins_section = wp_results.split("Plugin Information:")[1]
                            current_plugin = []
                            
                            for line in plugins_section.strip().split('\n'):
                                if line.strip():
                                    current_plugin.append(line.strip())
                                    if len(current_plugin) == 2:
                                        st.code('\n'.join(current_plugin))
                                        current_plugin = []
                    else:
                        st.info("WordPress bilgileri bulunamadı.")

            if moodle_check:
                with st.expander("📚 Moodle Tarama Sonuçları", expanded=True):
                    moodle_results = capture_output(MoodleCrawl.crawl, target_url)
                    if "Version Code:" in moodle_results:
                        st.code(moodle_results)
                    else:
                        st.info("Moodle bilgileri bulunamadı.")
        st.success("✅ Tarama başarıyla tamamlandı!")

if __name__ == "__main__":
    main()
    
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='position: fixed; bottom: 0; left: 0; padding: 10px; width: 300px;'>"
                   "<p style='text-align: center; color: #FFA500;'>Geliştirici: Yasin Yaşar</p>"
                   "<div style='display: flex; justify-content: center; gap: 10px;'>"
                   "<a href='https://www.linkedin.com/in/yasinyasarai/' target='_blank'>"
                   "<img src='https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white' height='25'/></a>"
                   "<a href='https://www.instagram.com/yyasar.yasin/' target='_blank'>"
                   "<img src='https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white' height='25'/></a>"
                   "</div></div>", 
                   unsafe_allow_html=True)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
    </style>
    """, unsafe_allow_html=True)