export type ValidationRule = {
  val: unknown;
  reg: RegExp | ((value: unknown) => boolean | Promise<boolean>);
  msg: string;
};
