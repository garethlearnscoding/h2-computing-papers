# 1. Abandon securetest.py in favor of RestrictedPython
1. __Doesn't work__ in stopping builtins.open

    outfile_test.py:
    ```
    ...

    SecureTest()
    class TestTaskSkibidiSigma(unittest.TestCase):
        def testBuiltinFunctions(self):
            # [TRUNCATED TESTS FOR EVAL AND EXEC]
            with self.assertRaises(Exception, msg="Exception for open should be raised"):
                with open(__file__) as f:
                    print(type(f))
                    print(f.read(48))
                    print("")
                    pass
    ```
    Output (yes this is output and not file):
    ```
    <class '_io.TextIOWrapper'>
    import unittest

    from python_testcase_functions

    Test failed in TestTaskSkibidiSigma: Exception not raised : Exception for open should be raised 
    ```
2. RestrictedPython patches the code at the AST layer.
    * This should technically mean that it can even patch/block stuff beyond what is possible in normal `unittest.mock.patch` (idk man i'm not an expert)
3. RestrictedPython also takes in user code as a string, which is the format we get.
    * We get the formats as a list of cells (i.e. strings) that we can also execute 1 by 1 in RestrictedPython while passing on \_\_globals\_\_
4. __Security__: RestrictedPython is more up-to-date in terms of python exploits and is more likely to be much safer than we can implement (even with AI!)