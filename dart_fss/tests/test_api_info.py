# -*- coding: utf-8 -*-
from dart_fss.errors.errors import NoDataReceived


def test_cndl_capl_scrits_nrdmp_blce(dart):
    try:
        _ = dart.api.info.cndl_capl_scrits_nrdmp_blce(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_unrst_exctv_mendng_sttus(dart):
    try:
        _ = dart.api.info.unrst_exctv_mendng_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="01343735",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_cprnd_nrdmp_blce(dart):
    try:
        _ = dart.api.info.cprnd_nrdmp_blce(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_srtpd_psndbt_nrdmp_blce(dart):
    try:
        _ = dart.api.info.srtpd_psndbt_nrdmp_blce(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_entrprs_bil_scrits_nrdmp_blce(dart):
    try:
        _ = dart.api.info.entrprs_bil_scrits_nrdmp_blce(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_det_scrits_isu_acmslt(dart):
    try:
        _ = dart.api.info.det_scrits_isu_acmslt(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_prvsrp_cptal_use_dtls(dart):
    try:
        _ = dart.api.info.prvsrp_cptal_use_dtls(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00382199",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_pssrp_cptal_use_dtls(dart):
    try:
        _ = dart.api.info.pssrp_cptal_use_dtls(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00382199",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_drctr_adt_all_mendng_sttus_gmtsck_confm_amount(dart):
    try:
        _ = dart.api.info.drctr_adt_all_mendng_sttus_gmtsck_confm_amount(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_drctr_adt_all_mendng_sttus_mendng_pymntamt_ty_cl(dart):
    try:
        _ = dart.api.info.drctr_adt_all_mendng_sttus_mendng_pymntamt_ty_cl(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_stock_totqy_sttus(dart):
    try:
        _ = dart.api.info.stock_totqy_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_accnut_adtor_nm_nd_adt_opinion(dart):
    try:
        _ = dart.api.info.accnut_adtor_nm_nd_adt_opinion(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_adt_servc_cncls_sttus(dart):
    try:
        _ = dart.api.info.adt_servc_cncls_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_accnut_adtor_non_adt_servc_cncls_sttus(dart):
    try:
        _ = dart.api.info.accnut_adtor_non_adt_servc_cncls_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_outcmpny_drctr_nd_change_sttus(dart):
    try:
        _ = dart.api.info.outcmpny_drctr_nd_change_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="01343735",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_new_capl_scrits_nrdmp_blce(dart):
    try:
        _ = dart.api.info.new_capl_scrits_nrdmp_blce(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2019",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_irds_sttus(dart):
    try:
        _ = dart.api.info.irds_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_alot_matter(dart):
    try:
        _ = dart.api.info.alot_matter(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_tesstk_acqs_dsps_sttus(dart):
    try:
        _ = dart.api.info.tesstk_acqs_dsps_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_hyslr_sttus(dart):
    try:
        _ = dart.api.info.hyslr_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_hyslr_chg_sttus(dart):
    try:
        _ = dart.api.info.hyslr_chg_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_mrhl_sttus(dart):
    try:
        _ = dart.api.info.mrhl_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_exctv_sttus(dart):
    try:
        _ = dart.api.info.exctv_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_emp_sttus(dart):
    try:
        _ = dart.api.info.emp_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_hmv_audit_indvdl_by_sttus(dart):
    try:
        _ = dart.api.info.hmv_audit_indvdl_by_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_hmv_audit_all_sttus(dart):
    try:
        _ = dart.api.info.hmv_audit_all_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_indvdl_by_pay(dart):
    try:
        _ = dart.api.info.indvdl_by_pay(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_otr_cpr_invstmnt_sttus(dart):
    try:
        _ = dart.api.info.otr_cpr_invstmnt_sttus(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e
