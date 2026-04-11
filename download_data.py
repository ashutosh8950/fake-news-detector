"""
Download dataset from public Kaggle mirror on HuggingFace.
Run this once before training: python download_data.py
"""

import os
import requests
import zipfile
import io

DATA_DIR = "data"
FILES = {
    "Fake.csv": "https://raw.githubusercontent.com/lutzhamel/fake-news/refs/heads/master/data/fake_or_real_news.csv",
}

# Primary source: GitHub hosted version of WELFake dataset
WELFACE_URL = "https://huggingface.co/datasets/GonzaloA/fake_news/resolve/main/train.csv"

# Fallback: Use a small embedded sample dataset for demo purposes
SAMPLE_FAKE = [
    ("BREAKING: Obama Signs Executive Order Banning Pledge of Allegiance In Schools Nationwide", "In a shocking move, President Obama has signed an executive order outlawing the Pledge of Allegiance from all U.S. public school classrooms. Obama cited the phrase 'one nation under God' as a violation of the constitutionally mandated separation of church and state...", "politics"),
    ("Pope Francis Shocks World, Endorses Donald Trump for President", "Pope Francis, head of the Catholic Church, has made a stunning political statement by formally endorsing Republican presidential nominee Donald Trump in a bombshell video released by the Vatican.", "News"),
    ("Donald Trump Protester Speaks Out: 'I Was Paid $3,500 To Protest Trump's Rally'", "A recent college graduate, told MSNBC's Rachel Maddow that she was paid $3,500 by 'a group of people' to protest at a  Trump rally near her home.", "politics"),
    ("CNN Panelist Calls For Violence Against Trump Supporters", "A CNN panelist suggested that Trump supporters deserve violence. The radical left is getting more and more extreme every single day.", "News"),
    ("Hillary Clinton In 2013: I Would Like To See People Like Donald Trump Run For Office", "Hillary Clinton, who we all know had extremely private opinions about Donald Trump for years, was caught on tape saying how much she would love to see someone like The Donald run for office.", "politics"),
    ("WikiLeaks Exposes Hillary Clinton Asking Saudi Arabia For 50% Of What She Has Stolen From Haiti", "WikiLeaks has exposed Hillary Clinton asking Saudi Arabia for 50% of stolen Haiti funds, claiming the cash is rightfully hers.", "politics"),
    ("Trump Secretly Owns Multiple Shares In CNN And Fox News Combined", "Exclusive: New documents reveal Donald Trump secretly owns substantial shares in both CNN and Fox News parent companies, explaining his unique media relationships.", "News"),
    ("FBI Anti-Trump Agent Peter Strzok Had Affair, His Wife Is Now Demanding Divorce", "Lisa Page's texts reveal agent Strzok's affair with her while working on the Trump investigation. His wife is now demanding divorce.", "politics"),
    ("PROOF THAT OBAMA IS GAY: Video Of His 'Body Man' Reggie Love Reveals Truth", "A jaw-dropping video has emerged showing Barack Obama's personal aide Reggie Love in a very compromising position that reveals the true nature of their relationship.", "politics"),
    ("George Soros Funded Organization Plotting To Overthrow The US Government", "Secret documents reveal that George Soros is funding a massive, coordinated effort to collapse the United States government and replace it with a globalist regime.", "politics"),
]

SAMPLE_TRUE = [
    ("U.S. military to accept transgender recruits on Monday: Pentagon", "WASHINGTON (Reuters) - The U.S. military will begin accepting transgender recruits on Monday as planned, the Pentagon said on Friday, after President Donald Trump's administration decided not to appeal a federal court ruling.", "politicsNews"),
    ("Senior U.S. Republican senator: 'Let Mr. Mueller do his job'", "WASHINGTON (Reuters) - The special counsel investigating possible ties between the 2016 Trump campaign and Russia should be allowed to complete his work, a senior Republican senator said on Sunday.", "politicsNews"),
    ("FBI Russia probe helped by Australian diplomat tip-off: report", "WASHINGTON (Reuters) - Trump campaign adviser George Papadopoulos told an Australian diplomat in May 2016 that Russia had thousands of emails that would embarrass Hillary Clinton, the New York Times reported on Saturday.", "politicsNews"),
    ("Trump wants Postal Service to charge 'much more' for Amazon shipments", "SEATTLE/WASHINGTON (Reuters) - President Donald Trump called on the U.S. Postal Service on Friday to charge 'much more' for delivering Amazon.com Inc packages, picking his latest fight with the e-commerce giant.", "politicsNews"),
    ("White House, Congress prepare for high-stakes showdown over spending", "WASHINGTON (Reuters) - The White House and Congress were preparing on Friday for a high-stakes budget showdown that could lead to a government shutdown.", "politicsNews"),
    ("Pence says U.S. will stand with Poland against Russian aggression", "WARSAW (Reuters) - Vice President Mike Pence said on Saturday that the United States would stand with Poland against Russian aggression as he kicked off a trip to Central Europe.", "worldnews"),
    ("U.S., South Korea to hold annual joint military exercises", "SEOUL (Reuters) - The United States and South Korea said on Friday they would hold annual joint military exercises, shrugging off North Korean threats and calls from China and Russia to cancel them.", "worldnews"),
    ("Fed's Fischer says gradual U.S. rate hike path still appropriate", "WASHINGTON (Reuters) - The Federal Reserve's path of gradually increasing interest rates remains appropriate as the central bank works towards its policy goals, Fed Vice Chairman Stanley Fischer said on Friday.", "politicsNews"),
    ("EU sees need for more oversight of big tech platforms: paper", "BRUSSELS (Reuters) - The European Union sees a need to have more oversight over big technology companies, according to a draft paper prepared for a meeting of EU ministers to be held on Friday.", "politicsNews"),
    ("North Korea fires what appears to be intercontinental ballistic missile", "SEOUL/TOKYO (Reuters) - North Korea on Tuesday fired what appeared to be its most advanced intercontinental ballistic missile yet, which came down in waters off Japan after flying for about 50 minutes.", "worldnews"),
]

def create_sample_data():
    """Create a small sample dataset for demo purposes."""
    import pandas as pd

    os.makedirs(DATA_DIR, exist_ok=True)

    fake_rows = [{"title": t, "text": tx, "subject": s, "date": "January 1, 2017"} for t, tx, s in SAMPLE_FAKE]
    true_rows = [{"title": t, "text": tx, "subject": s, "date": "January 1, 2017 "} for t, tx, s in SAMPLE_TRUE]

    pd.DataFrame(fake_rows).to_csv(os.path.join(DATA_DIR, "Fake.csv"), index=False)
    pd.DataFrame(true_rows).to_csv(os.path.join(DATA_DIR, "True.csv"), index=False)
    print(f"✅ Created sample dataset: {len(fake_rows)} fake + {len(true_rows)} true articles")
    return True

def download_full_dataset():
    """Try to download the full dataset from public sources."""
    import csv, io as _io
    os.makedirs(DATA_DIR, exist_ok=True)

    # Try HuggingFace WELFake dataset
    print("📥 Attempting to download dataset from HuggingFace...")
    try:
        resp = requests.get(WELFACE_URL, timeout=60, stream=True)
        if resp.status_code == 200:
            import pandas as pd
            # Use quoting to handle embedded commas/newlines inside fields
            df = pd.read_csv(
                _io.StringIO(resp.text),
                quoting=csv.QUOTE_ALL,
                on_bad_lines='skip',
                engine='python',
            )
            print(f"   Downloaded {len(df)} rows. Columns: {list(df.columns)}")
            if 'label' in df.columns and 'text' in df.columns:
                df_fake = df[df['label'] == 0][['title', 'text']].copy()
                df_true = df[df['label'] == 1][['title', 'text']].copy()
                df_fake['subject'] = 'News'
                df_fake['date']    = 'January 1, 2017'
                df_true['subject'] = 'politicsNews'
                df_true['date']    = 'January 1, 2017 '
                df_fake.to_csv(os.path.join(DATA_DIR, "Fake.csv"), index=False)
                df_true.to_csv(os.path.join(DATA_DIR, "True.csv"), index=False)
                print(f"✅ Full dataset saved: {len(df_fake)} fake + {len(df_true)} true")
                return True
    except Exception as e:
        print(f"   HuggingFace download failed: {e}")

    print("⚠️  Could not download full dataset.")
    print("   Using built-in sample data (small dataset — for demo only).")
    print()
    print("   For best accuracy (~99%), manually place Fake.csv and True.csv in the 'data/' folder.")
    print("   Download from: https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset")
    return False

if __name__ == "__main__":
    fake_path = os.path.join(DATA_DIR, "Fake.csv")
    true_path = os.path.join(DATA_DIR, "True.csv")

    if os.path.exists(fake_path) and os.path.exists(true_path):
        import pandas as pd
        fake_count = len(pd.read_csv(fake_path))
        true_count = len(pd.read_csv(true_path))
        print(f"✅ Dataset already exists: {fake_count} fake + {true_count} true articles")
    else:
        success = download_full_dataset()
        if not success:
            create_sample_data()
