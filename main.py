import streamlit as st
import sqlite3
from datetime import datetime

class CRM:
    def __init__(self):
        self.conn = sqlite3.connect("gezen_tavuk_crm.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabloları oluşturmak için SQL sorgularını buraya ekleyin
        query_create_members = """
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            subscription_type TEXT,
            egg_type TEXT,
            delivery_day TEXT,
            delivery_time TEXT,
            phone_number TEXT
        )
        """

        query_create_egg_types = """
        CREATE TABLE IF NOT EXISTS egg_types (
            egg_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            unit_price REAL
        )
        """

        try:
            self.cursor.execute(query_create_members)
            self.cursor.execute(query_create_egg_types)
            self.conn.commit()
        except sqlite3.Error as e:
            print("Tablo oluşturulurken bir hata oluştu:", str(e))

    def run(self):
        st.sidebar.title("Gezen Tavuk Yumurtası CRM")
        while True:
            choice = st.sidebar.radio("Menü", ["Üyelik Ekle", "Yumurta Türü Ekle", "Üyeleri Listele",
                                               "Yumurtaları Listele", "Ana Sayfa", "Üye Sil ve Düzenle",
                                               "Yumurta Sil ve Düzenle"])

            if choice == "Üyelik Ekle":
                self.add_membership()
            elif choice == "Yumurta Türü Ekle":
                self.add_egg_type()
            elif choice == "Üyeleri Listele":
                self.list_members()
            elif choice == "Yumurtaları Listele":
                self.list_eggs()
            elif choice == "Ana Sayfa":
                self.show_dashboard()
            elif choice == "Üye Sil ve Düzenle":
                self.edit_member()
            elif choice == "Yumurta Sil ve Düzenle":
                self.edit_egg_type()

    def add_membership(self):
        st.title("Üyelik Ekle")
        member_name = st.text_input("Üye İsmi:")
        subscription_type = st.selectbox("Abonelik Türü:", ["Aylık", "Haftalık"])
        egg_type = st.text_input("Yumurta Türü:")
        delivery_day = st.text_input("Teslimat Günü:")
        delivery_time = st.text_input("Teslimat Saati:")
        phone_number = st.text_input("Üye Telefon Numarası:")

        if st.button("Üyeliği Ekle"):
            # Veritabanına üye eklemek için SQL sorgusunu oluşturun
            query = "INSERT INTO members (name, subscription_type, egg_type, delivery_day, delivery_time, phone_number) VALUES (?, ?, ?, ?, ?, ?)"
            values = (member_name, subscription_type, egg_type, delivery_day, delivery_time, phone_number)

            try:
                self.cursor.execute(query, values)
                self.conn.commit()
                st.success("Üye başarıyla eklendi!")
            except sqlite3.Error as e:
                st.error("Üye eklenirken bir hata oluştu: {}".format(str(e)))

    def add_egg_type(self):
        st.title("Yumurta Türü Ekle")
        egg_name = st.text_input("Yumurta İsmi:")
        unit_price = st.number_input("Adet Fiyatı:")

        if st.button("Yumurta Türü Ekle"):
            # Veritabanına yumurta türü eklemek için SQL sorgusunu oluşturun
            query = "INSERT INTO egg_types (name, unit_price) VALUES (?, ?)"
            values = (egg_name, unit_price)

            try:
                self.cursor.execute(query, values)
                self.conn.commit()
                st.success("Yumurta türü başarıyla eklendi!")
            except sqlite3.Error as e:
                st.error("Yumurta türü eklenirken bir hata oluştu: {}".format(str(e)))

    def list_members(self):
        st.title("Üyeler")
        # Veritabanından üyeleri almak için SQL sorgusunu oluşturun
        query = "SELECT * FROM members"
        self.cursor.execute(query)
        members = self.cursor.fetchall()

        if members:
            st.table(members)
        else:
            st.info("Kayıtlı üye bulunmamaktadır.")

    def list_eggs(self):
        st.title("Yumurtalar")
        # Veritabanından yumurtaları almak için SQL sorgusunu oluşturun
        query = "SELECT * FROM egg_types"
        self.cursor.execute(query)
        eggs = self.cursor.fetchall()

        if eggs:
            st.table(eggs)
        else:
            st.info("Kayıtlı yumurta türü bulunmamaktadır.")

    def show_dashboard(self):
        st.title("Ana Sayfa")

        # Günün teslimatları için SQL sorgusunu oluşturun
        today = datetime.now().date()
        query_deliveries = "SELECT * FROM members WHERE delivery_day = ?"
        self.cursor.execute(query_deliveries, (today,))
        deliveries = self.cursor.fetchall()

        st.header("Günün Teslimatları")
        if deliveries:
            for delivery in deliveries:
                member_id, name, subscription_type, egg_type, delivery_day, delivery_time, phone_number = delivery
                st.write("- {} - {} ({}, {})".format(name, egg_type, delivery_day, delivery_time))
        else:
            st.write("Bugün teslimat yapılacak üye bulunmamaktadır.")

        # Aylık ve günlük kazanç için SQL sorgularını oluşturun
        query_monthly_earnings = "SELECT SUM(unit_price) FROM egg_types"
        query_daily_earnings = "SELECT SUM(unit_price) FROM egg_types WHERE egg_type_id IN (SELECT DISTINCT egg_type FROM members)"

        self.cursor.execute(query_monthly_earnings)
        monthly_earnings = self.cursor.fetchone()[0] or 0

        self.cursor.execute(query_daily_earnings)
        daily_earnings = self.cursor.fetchone()[0] or 0

        # Toplam üye sayısı için SQL sorgusunu oluşturun
        query_total_members = "SELECT COUNT(*) FROM members"
        self.cursor.execute(query_total_members)
        total_members = self.cursor.fetchone()[0]

        st.header("Kazanç ve İstatistikler")
        st.write("Aylık Kazanç: ${}".format(monthly_earnings))
        st.write("Günlük Kazanç: ${}".format(daily_earnings))
        st.write("Toplam Üye Sayısı: {}".format(total_members))

    def edit_member(self):
        st.title("Üye Düzenle")
        member_id = st.text_input("Düzenlemek istediğiniz üyenin ID'sini girin:")

        # Veritabanından belirtilen üyenin bilgilerini almak için SQL sorgusunu oluşturun
        query_select_member = "SELECT * FROM members WHERE member_id = ?"
        self.cursor.execute(query_select_member, (member_id,))
        member = self.cursor.fetchone()

        if not member:
            st.warning("Belirtilen ID'ye sahip üye bulunamadı.")
            return

        _, name, subscription_type, egg_type, delivery_day, delivery_time, phone_number = member

        st.subheader("Üye Bilgileri:")
        st.write("1. İsim: {}".format(name))
        st.write("2. Abonelik Türü: {}".format(subscription_type))
        st.write("3. Yumurta Türü: {}".format(egg_type))
        st.write("4. Teslimat Günü: {}".format(delivery_day))
        st.write("5. Teslimat Saati: {}".format(delivery_time))
        st.write("6. Telefon Numarası: {}".format(phone_number))

        choice = st.text_input("Düzenlemek istediğiniz öğenin numarasını girin (Çıkış için '0'): ")

        if choice == "0":
            return
        elif choice == "1":
            name = st.text_input("Yeni İsim:")
        elif choice == "2":
            subscription_type = st.selectbox("Yeni Abonelik Türü:", ["Aylık", "Haftalık"])
        elif choice == "3":
            egg_type = st.text_input("Yeni Yumurta Türü:")
        elif choice == "4":
            delivery_day = st.text_input("Yeni Teslimat Günü:")
        elif choice == "5":
            delivery_time = st.text_input("Yeni Teslimat Saati:")
        elif choice == "6":
            phone_number = st.text_input("Yeni Telefon Numarası:")
        else:
            st.warning("Geçersiz bir seçenek. Tekrar deneyin.")
            return

        # Veritabanındaki üye bilgilerini güncellemek için SQL sorgusunu oluşturun
        query_update_member = "UPDATE members SET name=?, subscription_type=?, egg_type=?, delivery_day=?, delivery_time=?, phone_number=? WHERE member_id=?"
        values = (name, subscription_type, egg_type, delivery_day, delivery_time, phone_number, member_id)

        try:
            self.cursor.execute(query_update_member, values)
            self.conn.commit()
            st.success("Üye bilgileri başarıyla güncellendi!")
        except sqlite3.Error as e:
            st.error("Üye bilgilerini güncellerken bir hata oluştu: {}".format(str(e)))

    def edit_egg_type(self):
        st.title("Yumurta Türü Düzenle")
        egg_type_id = st.text_input("Düzenlemek istediğiniz yumurta türünün ID'sini girin:")

        # Veritabanından belirtilen yumurta türünün bilgilerini almak için SQL sorgusunu oluşturun
        query_select_egg_type = "SELECT * FROM egg_types WHERE egg_type_id = ?"
        self.cursor.execute(query_select_egg_type, (egg_type_id,))
        egg_type = self.cursor.fetchone()

        if not egg_type:
            st.warning("Belirtilen ID'ye sahip yumurta türü bulunamadı.")
            return

        _, egg_name, unit_price = egg_type

        st.subheader("Yumurta Türü Bilgileri:")
        st.write("1. Yumurta İsmi: {}".format(egg_name))
        st.write("2. Adet Fiyatı: {}".format(unit_price))

        choice = st.text_input("Düzenlemek istediğiniz öğenin numarasını girin (Çıkış için '0'): ")

        if choice == "0":
            return
        elif choice == "1":
            egg_name = st.text_input("Yeni Yumurta İsmi:")
        elif choice == "2":
            unit_price = st.number_input("Yeni Adet Fiyatı:")
        else:
            st.warning("Geçersiz bir seçenek. Tekrar deneyin.")
            return

        # Veritabanındaki yumurta türü bilgilerini güncellemek için SQL sorgusunu oluşturun
        query_update_egg_type = "UPDATE egg_types SET name=?, unit_price=? WHERE egg_type_id=?"
        values = (egg_name, unit_price, egg_type_id)

        try:
            self.cursor.execute(query_update_egg_type, values)
            self.conn.commit()
            st.success("Yumurta türü bilgileri başarıyla güncellendi!")
        except sqlite3.Error as e:
            st.error("Yumurta türü bilgilerini güncellerken bir hata oluştu: {}".format(str(e)))

# Uygulamayı başlat
crm_app = CRM()
crm_app.run()
