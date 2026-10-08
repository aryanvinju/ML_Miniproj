# Public real-data source

`breast_qlq_c30.xlsx` is the original CC0 dataset file from Carmona-Bayonas et al. (2021), Figshare item [10.6084/m9.figshare.14681274](https://doi.org/10.6084/m9.figshare.14681274). Download it with `python -m src.download_data` or from `https://ndownloader.figshare.com/files/28199136`. Expected MD5: `d7733d01c6982a3f68e77817f5666276`. The workbook is excluded from Git so the public repository contains code and derived results without duplicating patient-level data.

The linked [npj Breast Cancer article](https://doi.org/10.1038/s41523-021-00296-8) describes a 339-patient database; 219 had the end-of-treatment health-status score and 217 had both baseline and end scores needed for this project's decline label. The data are de-identified but should still be handled as research data. The repository does not combine rows with the other two workbooks because they lack a documented shared patient identifier.

`src/train_real.py` reads this workbook directly. It excludes every `_end` field from model inputs. The target is a decline of at least 10 points in EORTC QLQ-C30 global health status between baseline and treatment completion. This differs from the Stanford paper's PROMIS GPH target and its during-treatment timing.
