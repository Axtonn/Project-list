function validatePassword(password) {
  const minLength = /.{8,}/;
  const hasLower = /[a-z]/;
  const hasUpper = /[A-Z]/;
  const hasNumber = /\d/;
  const hasSpecial = /[\W_]/;

  return (
    minLength.test(password) &&
    hasLower.test(password) &&
    hasUpper.test(password) &&
    hasNumber.test(password) &&
    hasSpecial.test(password)
  );
}

module.exports = { validatePassword };
