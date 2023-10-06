import spacy


def main():
    # table_data = extract_tables_from_pdf("/home/jud/projects/docextract/data/abc.pdf")
    nlp = spacy.load("en_core_web_trf")
    doc = nlp("""      “Threshold Amount” means, with respect to Party A, an amount equal to USD 50,000,000 (or the equivalent in
      another currency, currency unit or combination thereof) and with respect to Party B an amount equal to the lesser
      of 3% of Net Asset Value (as defined hereafter) and USD 50,000,000 (or the equivalent in another currency,
      currency unit or combination thereof).""")
    # print([(w.text, w.pos_) for w in doc])
    text_hdr = "Text"
    pos_hdr = "POS"
    tag_hdr = "TAG"
    dep_hdr = "DEP"
    lemma_hdr = "Lemma"
    dash_tbl = "="
    print(f"{text_hdr:<14} | {pos_hdr:<7} | {tag_hdr:<10} | {dep_hdr:<10} | {lemma_hdr:<14}")
    print(f"{dash_tbl:-<14}-|-{dash_tbl:-<7}-|-{dash_tbl:-<10}-|-{dash_tbl:-<10}-|-{dash_tbl:-<14}")
    for token in doc:
        if token.pos_ == "SPACE":
            continue
        if token.pos_ == "PUNCT":
            continue
        print(f"{token.text:<14} | {token.pos_:<7} | {token.tag_:<10} | {token.dep_:<10} | {token.lemma_:<14}")
        if token.is_stop:
            print("")

    print("\n\nENTITIES:\n\n")
    for ent in doc.ents:
        print(f"{ent.text:<20} | {ent.label_}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open("asdf") as file:
        file.readlines()

    main()
