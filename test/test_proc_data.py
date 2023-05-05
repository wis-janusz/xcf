import xcf

def test_split_df(test_df, test_split):
    [split1,split2,split3] = xcf.split_df(test_df)

    assert split1.equals(test_split[0])
    assert split2.equals(test_split[1])
    assert split3.equals(test_split[2])
