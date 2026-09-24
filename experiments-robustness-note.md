# Robustness and overfitting interpretation

This project contains no learned model, fitted coefficient, training set, or hyperparameter selected to maximize a reported benchmark.  The relevant analogue of overfitting is narrower: implementing only the hand-written examples, tuning generators after seeing failures, or using the same code path as both optimizer and oracle.

The artifact therefore separates evidence by failure mode:

- general claims are supported by hand-written proofs;
- exactness on small instances is checked by explicit enumeration independent of the dynamic program;
- serialized objects are interpreted by a separate implementation and challenged with guaranteed-changing negative mutations;
- extraction is checked on a restricted operational IR with negative controls;
- confirmed generated inputs and seeds are preserved, and exploratory outputs are not silently promoted;
- search limits fail closed rather than converting truncation into an optimality claim;
- the corpus audit reports structural signatures and exact duplicates instead of calling a post-hoc partition a preregistered holdout.

These measures reduce example- and implementation-specific overfitting.  They do not establish performance on production compiler workloads, which remains outside the paper's claim.
