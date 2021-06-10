# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import csv
import numpy as np
import tokenization

csv_separator = ';'
icd_column_name = 'CID_CLASSIFICACAO'
group_column_name = 'CID_GRUPO'


def get_group(icd_classification, grouping_entries):
    group = None

    icd_classification = icd_classification.split('#')[0]

    if icd_classification != '-1':
        for index, row in grouping_entries.iterrows():
            if icd_classification >= row['category_start'] and icd_classification <= row['category_end']:
                group = row['chapter']
                break
    else:
        group = '-1'

    assert group is not None, 'Error: ICD classification informed ("%s") is inconsistent with CID-10 standard.' % icd_classification

    return group


def get_group_from_icd(icd_classifications_entries, grouping_entries):
    groups_from_icd_classifications = []

    for icd_classifications_entry in icd_classifications_entries:
        if icd_classifications_entry != '':
            icd_classifications = icd_classifications_entry.split('\n')
        else:
            icd_classifications = ''

        group_from_icd_classification = []
        for icd_classification in icd_classifications:
            group = get_group(icd_classification, grouping_entries)

            group_from_icd_classification.append(group)

        group_from_icd_classification_textual = '\n'.join(group_from_icd_classification)

        groups_from_icd_classifications.append(group_from_icd_classification_textual)

    return groups_from_icd_classifications


def get_icd(disease, icd_entries):
    disease_preprocessed_stem = tokenization.preprocess_text(disease, lowercase=True, remove_stopwords=True,
                                                             stemmize=True, strip_accents=True, expand_contractions=False,
                                                             use_min_word_length=True, join_tokens_by_char=".*")

    common_words = "crise síndrome traumatismo trauma tendência desidratação bilateral deficiência entupimento dilatada difusa grave mecânica comorbidade multiforme"
    common_words_stems = tokenization.preprocess_text(common_words, lowercase=True, remove_stopwords=False,
                                                      stemmize=True, strip_accents=True, expand_contractions=False,
                                                      use_min_word_length=False, join_tokens_by_char=None)

    disease_preprocessed_stem = disease_preprocessed_stem.replace('canc', 'neoplas')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('adenocarcinom', 'neoplas')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('metastas', 'neoplas')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('oncolog', 'neoplas')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('lesion', 'les')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('grav', 'gravid')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('gestant', 'gravid')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('insuficient', 'insuficien')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('coronarian', 'cardiac')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('avc', 'acident.*vascul.*cerebr')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('cefal', 'cefaleia$')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('lombociatalg', 'dorsalg')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('incontinent', 'incontinen')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('meningiom', 'neoplas.*mening')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('demencial', 'demenc')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('arterioescleros', 'aterosclerose')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('cimitarr', 'malformac.*congenit')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('suic', 'les.*autoprovoc')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('reconstru', 'cirurg')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('linfonod', 'vol.*gang.*linf')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('tort', 'deform.*congenit')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('tetrapares', 'tetrapleg')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('afas', 'disturb.*fal')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('bronqueolit', 'bronquiolit')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('lombalg', 'dorsalg')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('surt.*psicot.*delir', 'transtorn.*psicot')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('osteorradionecros', 'osteonecros')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('discal', 'disc')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('extrusa', 'transtorn')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('anorex', 'transtorn.*alim')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('pneumopat', 'pulmon.*interstic')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('cardiopat.*congenit', 'malformac.*corac')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('plaquetopen', 'purpur')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('sobrepes', 'obesidad')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('congesta.*pulmon', 'edem.*pulmon')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('depressa', 'depres')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('neuromielit', 'neurit')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('engravidid', 'gravid')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('gravididez', 'gravid')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('hipoton', 'ton.*muscul')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('deficient.*visual', 'disturb.*visu')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('melen', 'doenc.*aparelh.*digestiv')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('hematemes', 'doenc.*aparelh.*digestiv')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('rompiment', 'distens')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('uterin', 'uter')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('adenomios', 'endometrios')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('osteocondrom', 'osteocondros')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('pulmon', 'pulm')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('lesion', 'les')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('sindrom.*poland', 'malformac.*osteomusc')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('sindrom.*schnitzl', 'urticar')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('antevers', 'malformac.*quadr')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('broncoespasm', 'bronqu.*agud')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('sindrom.*hakim.*adams', 'hidrocef')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('citomegaloviros', 'doenc.*citomegalovir')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('taquidispn', 'anorm.*resp')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('condrossarcom.*distal', 'neoplas.*oss.*cartil')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('pseudoartros', 'consol.*frat')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('nefrolitias', 'calcul.*rim')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('aracnoidit.*lomb', 'doenc.*med.*esp')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('traumat.*raquimedul', 'traumat.*nerv.*cerv')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('esteatos.*hepat', 'degen.*fig')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('gigantomast', 'hipertrof.*mam')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('acuidad.*visual', 'disturb.*vis')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('rinosinusit', 'sinusit.*agud')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('otomastoidit.*colesteatomat', 'mastoidit')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('mielomeningocel.*lomb', 'espinh.*bif')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('sindrom.*olgivi', 'obstr.*intestin')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('coronariopat', 'isquem.*cron.*corac')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('pedr.*vesicul', 'colelitias')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('neocardiopat.*dilat', 'cardiomiopat')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('opacific.*cristalin', 'transt.*cristal')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('discopat.*degener', 'transt.*especif.*disc')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('micrognat', 'doenc.*maxil')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('taquidispn', 'anormal.*resp')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('hepatopat', 'outr.*doenc.*figad')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('hipoacus.*neurossensorial', 'perd.*audic')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('meduloblastom', 'neoplas.*encefal')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('hepatocarcinom', 'neoplas.*figad')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('superobes', 'obesidad')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('dislipidem', 'disturb.*metabol.*lipo')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('colangiocarcinom', 'neoplas.*figad')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('sacul.*aneurismat', 'outr.*aneurism')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('dorsodorsalg', 'dorsalg')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('esteatos.*hepat', 'outr.*doenc.*figad')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('meningomielocel', 'espinh.*bifid')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('glioblastom', 'neoplas.*encefal')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('hipertensa.*arterial', 'hipertensa.*secund')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('artroplast.*quadril', 'coxartros')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('gigantomast', 'hipertrof.*mam')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('impotent.*sexual', 'disfunc.*sex')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('osteoartros', 'artros.*primar')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('discopat.*cervical', 'transtorn.*disc.*cerv')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('claudic', 'anormalid.*march')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('surt.*psicot', 'transtorn.*psicotic.*agud')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('obit', 'mort.*instant')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('coreoatetos', 'paralis.*cerebr')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('retrognat.*mandibul', 'anomal.*mandibul')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('trombofil', 'defeit.*coagulac')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('psicopatolog', 'transtorn.*depressiv.*recorrent')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('amaurot', 'cegueir.*vis.*subnorm')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('flacidez.*generaliz', 'seguiment.*cirurg.*plastic')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('hialin', 'transtorn.*respirat')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('broncodisplas.*pulmon', 'displas.*broncopulm')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('diverticulit', 'doenc.*diverticul')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('osteopen', 'transtorn.*densidad')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('discopat', 'transtorn.*disc.*lombar')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('insuficien.*renal', 'insuficien.*ren.*agud')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('(', '')
    disease_preprocessed_stem = disease_preprocessed_stem.replace(')', '')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('+', '')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('\'', '')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('`', '')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('´', '')
    disease_preprocessed_stem = disease_preprocessed_stem.replace('"', '')

    disease_preprocessed_stem = disease_preprocessed_stem.rstrip('a').rstrip('o')

    icd_categories_disease_stem = icd_entries[icd_entries.description.str.contains(disease_preprocessed_stem)][['category', 'description']]

    icd = '-1'

    if icd_categories_disease_stem.size > 0:
        # icd = icd_categories_disease_stem['category'].iloc[0]
        icd = icd_categories_disease_stem['category'].iloc[0] + "#" + icd_categories_disease_stem['description'].iloc[0]
    else:
        disease_preprocessed_stem_parts = disease_preprocessed_stem.split('.*')

        uncommon_words_of_disease_preprocessed_stem = []
        for word_of_disease_preprocessed_stem in disease_preprocessed_stem_parts:
            is_common_word = False

            for common_word_stem in common_words_stems:
                if common_word_stem in word_of_disease_preprocessed_stem:
                    is_common_word = True
                    break

            if not is_common_word:
                uncommon_words_of_disease_preprocessed_stem.append(word_of_disease_preprocessed_stem)

        icd_categories_disease_stem_partial = None
        if len(uncommon_words_of_disease_preprocessed_stem) > 2:
            disease_preprocessed_stem_partial = '%s.*%s' % (uncommon_words_of_disease_preprocessed_stem[0], uncommon_words_of_disease_preprocessed_stem[-1])

            icd_categories_disease_stem_partial = icd_entries[icd_entries.description.str.contains(disease_preprocessed_stem_partial)][['category', 'description']]

            if icd_categories_disease_stem_partial.size == 0:
                icd_categories_disease_stem_partial = None

        if icd_categories_disease_stem_partial is None and len(uncommon_words_of_disease_preprocessed_stem) > 0:
            disease_preprocessed_stem_partial = uncommon_words_of_disease_preprocessed_stem[0]

            icd_categories_disease_stem_partial = icd_entries[icd_entries.description.str.contains(disease_preprocessed_stem_partial)][['category', 'description']]

            if icd_categories_disease_stem_partial.size == 0:
                icd_categories_disease_stem_partial = None

        if icd_categories_disease_stem_partial is not None:
            # icd = icd_categories_disease_stem_partial['category'].iloc[0]
            icd = icd_categories_disease_stem_partial['category'].iloc[0] + "#" + icd_categories_disease_stem_partial['description'].iloc[0]

    if icd == '-1':
        print('Unidentified disease: "%s" (stem: "%s")' % (disease, disease_preprocessed_stem))

    return icd


def get_icd_classification(diseases_entries, icd_entries):
    icd_classifications = []

    for diseases_entry in diseases_entries:
        if diseases_entry is not np.nan:
            diseases = diseases_entry.split('\n')
        else:
            diseases = ''

        icd_classification = []
        for disease in diseases:
            icd = get_icd(disease, icd_entries)

            icd_classification.append(icd)

        icd_classification_textual = '\n'.join(icd_classification)

        icd_classifications.append(icd_classification_textual)

    return icd_classifications


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description='Script to obtain the International Classification of Diseases (ICDs) '
                                          'classifications and a certain grouping from the extracted annotations.')

    args_parser.add_argument('icd_category_file_path', help='Path to the file containing the ICDs entries.')
    args_parser.add_argument('grouping_file_path', help='Path to the file containing the grouping entries.')
    args_parser.add_argument('extracted_annotations_file_path', help='Path to the file containing the extracted '
                                                                     'annotations.')
    args_parser.add_argument('disease_column_name', help='Disease column name in the file containing the extracted '
                                                         'annotations.')
    args_parser.add_argument('output_file_path', help='Path to the output file that will contain the ICDs '
                                                      'classifications and a certain grouping for the extracted '
                                                      'annotations entries.')

    args = args_parser.parse_args()

    icd_category_file_path = args.icd_category_file_path
    extracted_annotations_file_path = args.extracted_annotations_file_path
    disease_column_name = args.disease_column_name
    output_file_path = args.output_file_path
    grouping_file_path = args.grouping_file_path

    print('Loading ICDs entries from file "%s"...' % icd_category_file_path)
    icd_entries = pd.read_csv(icd_category_file_path, sep=csv_separator, header=0, index_col=None, dtype={'category': str,
                                                                                                 'description': str,
                                                                                                 'description_stem': str})

    print('Loading grouping entries from file "%s"...' % grouping_file_path)
    grouping_entries = pd.read_csv(grouping_file_path, sep=csv_separator, header=0, index_col=None, dtype={'chapter': str,
                                                                                                           'category_start': str,
                                                                                                           'category_end': str})

    print('Loading the extracted annotations from file "%s"...' % extracted_annotations_file_path)
    extracted_annotations = pd.read_csv(extracted_annotations_file_path, sep=csv_separator, header=0, index_col=None)

    assert disease_column_name in extracted_annotations.columns, 'Error: disease column name "%s" not found in file ' \
                                                                 '"%s".' % (disease_column_name, extracted_annotations_file_path)

    print('Obtaining ICDs classifications from the extracted annotations file...')
    diseases = extracted_annotations[disease_column_name].tolist()
    icd_classifications = get_icd_classification(diseases, icd_entries)

    extracted_annotations[icd_column_name] = icd_classifications

    print('Obtaining groups from ICDs classifications...')
    groups_from_icd_classifications = get_group_from_icd(icd_classifications, grouping_entries)

    extracted_annotations[group_column_name] = groups_from_icd_classifications

    print('Saving output file at "%s"...' % output_file_path)
    extracted_annotations.to_csv(output_file_path, sep=csv_separator, header=True, index=False, encoding='utf-8',
                                 quoting=csv.QUOTE_MINIMAL)
