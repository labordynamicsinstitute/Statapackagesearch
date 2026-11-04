/* For testing of the package only */
/* Each line below uses a keyword whose raw name in the crosswalk, or whose package, has underscores or capitals */

/* package and keyword both have underscores */
aic_model_selection y x

/* the longest keywords: 30 and 29 characters once cleaned, both from one package */
read_parameterestimates_indirect using y
read_parameterestimates_general using y

/* the keyword has a capital (qenvF) */
qenvF y x

/* the keyword is plain, the package has underscores (egen_inequal) */
egen y = theil(x)

/* the same word comes from two packages: tknz (tknz) and _tknz (wbopendata); both are reported */
tknz y x

/* the same word comes from two keywords of one package (_eststo, eststo in estout); it counts once */
eststo: y x

/* the same word comes from two packages that are one name once cleaned (joy_plot, joyplot); reported once */
joy_plot y x

/* a word that is too short is still dropped once it matches a keyword */
ie y x
