def main():
    app = Application.builder().token(BOT_TOKEN).build()
    # ... handlers ...
    app.run_polling()  # ← ЭТО ДОЛЖНО БЫТЬ!

if __name__ == "__main__":
    main()
