import itertools

from nltk.translate.bleu_score import corpus_bleu


def bleu_evaluation(nlg_results: list, reference: list) -> dict:
    """
    Computes BLEU score for 4 different evaluation sets, one for each period, i.e.
    today, tonight, tomorrow, tomorrow night. A final, global score is computed over all NLG periods.

    :param nlg_results: A list of dicts whose structure should match bulletin[lang]['tok'].
    :param reference: A list of dicts whose structure should match bulletin[lang]['tok']. The elements in the reference
    must be in the same order as that of nlg_results, i.e. nlg_result[0] is the NLG result corresponding to reference[0]
    and so on.
    :return: A dictionary containing evaluation results. There is a BLEU score for each of the following keys:
    today, tonight, tomorrow, tomorrow_night, and global. A BLEU score ranges from 0 (very poor) to 1 (perfect). If a
    period is not covered by the hypotheses and references, then its BLEU score will be -1 by convention.
    """
    assert len(nlg_results) == len(reference), "Results and references of different lengths!"

    periods = ['today', 'tonight', 'tomorrow', 'tomorrow_night']
    hypothesis_corpus = {x: [] for x in periods}
    reference_corpus = {x: [] for x in periods}
    bleu_result = {x: -1 for x in periods}

    for res, ref in zip(nlg_results, reference):
        assert res.keys() == ref.keys(), "Result and reference with different periods."
        for period in res.keys():
            hypothesis_corpus[period].append([item for sublist in res[period] for item in sublist])
            reference_corpus[period].append([[item for sublist in ref[period] for item in sublist]])

    for period in periods:
        if len(reference_corpus[period]) != 0:
            bleu_result[period] = corpus_bleu(reference_corpus[period], hypothesis_corpus[period])

    # global BLEU by concatenating all sentences and produce global score
    global_hypothesis = list(itertools.chain(*[hypothesis_corpus[x] for x in periods]))
    global_reference = list(itertools.chain(*[reference_corpus[x] for x in periods]))

    bleu_result['global'] = corpus_bleu(global_reference, global_hypothesis)

    return bleu_result
