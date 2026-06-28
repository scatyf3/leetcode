
1. same as 88, we should use the array tail's trick
2. but iterate through an array with invalid tail, we should menage our iterate index smartly, ie, we cannot simply use for syntax sugar, we should `i<=tail_index` and update index only when we do not do sweeping
3. an key takeaway is to use more while instead of for, because if you are using while, you need to update index mannually thus you can think about how you update your index.

