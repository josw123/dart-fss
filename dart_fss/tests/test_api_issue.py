# -*- coding: utf-8 -*-
from dart_fss.errors.errors import NoDataReceived


def test_df_ocr(dart):
    try:
        _ = dart.api.issue.df_ocr(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00112819",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_bsn_sp(dart):
    try:
        _ = dart.api.issue.bsn_sp(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00370006",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_ctrcvs_bgrq(dart):
    try:
        _ = dart.api.issue.ctrcvs_bgrq(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00367482",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_ds_rs_ocr(dart):
    try:
        _ = dart.api.issue.ds_rs_ocr(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="01102590",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_piic_decsn(dart):
    try:
        _ = dart.api.issue.piic_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00378363",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_fric_decsn(dart):
    try:
        _ = dart.api.issue.fric_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00121932",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_pifric_decsn(dart):
    try:
        _ = dart.api.issue.pifric_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00359395",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_cr_decsn(dart):
    try:
        _ = dart.api.issue.cr_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00121932",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_bnk_mngt_pcbg(dart):
    try:
        _ = dart.api.issue.bnk_mngt_pcbg(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00295857",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_lwst_lg(dart):
    try:
        _ = dart.api.issue.lwst_lg(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00164830",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_ov_lst_decsn(dart):
    try:
        _ = dart.api.issue.ov_lst_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00258801",
            bgn_de="20170101",
            end_de="20181231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_ov_dlst_decsn(dart):
    try:
        _ = dart.api.issue.ov_dlst_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00344287",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_ov_lst(dart):
    try:
        _ = dart.api.issue.ov_lst(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="01350869",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_ov_dlst(dart):
    try:
        _ = dart.api.issue.ov_dlst(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00344287",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_cvbd_is_decsn(dart):
    try:
        _ = dart.api.issue.cvbd_is_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00155355",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_bdwt_is_decsn(dart):
    try:
        _ = dart.api.issue.bdwt_is_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00140131",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_exbd_is_decsn(dart):
    try:
        _ = dart.api.issue.exbd_is_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00273420",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_bnk_mngt_pcsp(dart):
    try:
        _ = dart.api.issue.bnk_mngt_pcsp(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00141608",
            bgn_de="20160101",
            end_de="20161231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_wd_cocobd_is_decsn(dart):
    try:
        _ = dart.api.issue.wd_cocobd_is_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00382199",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_ast_inhtrf_etc_ptbk_opt(dart):
    try:
        _ = dart.api.issue.ast_inhtrf_etc_ptbk_opt(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00409681",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_otcpr_stk_invscr_trf_decsn(dart):
    try:
        _ = dart.api.issue.otcpr_stk_invscr_trf_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00230814",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_tgast_trf_decsn(dart):
    try:
        _ = dart.api.issue.tgast_trf_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00106395",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_tgast_inh_decsn(dart):
    try:
        _ = dart.api.issue.tgast_inh_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00160375",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_otcpr_stk_invscr_inh_decsn(dart):
    try:
        _ = dart.api.issue.otcpr_stk_invscr_inh_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00140131",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_bsn_trf_decsn(dart):
    try:
        _ = dart.api.issue.bsn_trf_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00131780",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_bsn_inh_decsn(dart):
    try:
        _ = dart.api.issue.bsn_inh_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00140131",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_tsstk_aq_trctr_cc_decsn(dart):
    try:
        _ = dart.api.issue.tsstk_aq_trctr_cc_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00382199",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_tsstk_aq_trctr_cns_decsn(dart):
    try:
        _ = dart.api.issue.tsstk_aq_trctr_cns_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00860332",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_tsstk_dp_decsn(dart):
    try:
        _ = dart.api.issue.tsstk_dp_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00121932",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_tsstk_aq_decsn(dart):
    try:
        _ = dart.api.issue.tsstk_aq_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00164742",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_stk_extr_decsn(dart):
    try:
        _ = dart.api.issue.stk_extr_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00219097",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_cmp_dvmg_decsn(dart):
    try:
        _ = dart.api.issue.cmp_dvmg_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00306135",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_cmp_dv_decsn(dart):
    try:
        _ = dart.api.issue.cmp_dv_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00266961",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_cmp_mg_decsn(dart):
    try:
        _ = dart.api.issue.cmp_mg_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00155319",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_stkrtbd_inh_decsn(dart):
    try:
        _ = dart.api.issue.stkrtbd_inh_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00173449",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_stkrtbd_trf_decsn(dart):
    try:
        _ = dart.api.issue.stkrtbd_trf_decsn(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00125965",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e
