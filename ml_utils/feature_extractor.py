# ml_utils/feature_extractor.py
import re
import tldextract
from urllib.parse import urlparse
import pandas as pd

SHORTENERS = {
    "bit.ly","goo.gl","tinyurl.com","ow.ly","t.co","bitly.com","buff.ly",
    "adf.ly","is.gd","soo.gd","s2r.co","tiny.cc"
}

IP_RE = re.compile(r'^(?:http[s]?://)?(?P<ip>(?:\d{1,3}\.){3}\d{1,3})(?:[:/]|$)')
PORT_RE = re.compile(r':([0-9]{2,5})')

def has_ip(url):
    return -1 if IP_RE.search(url) else 1

def long_url(url, short=54, medium=75):
    l = len(url)
    if l < short:
        return 1
    elif short <= l <= medium:
        return 0
    else:
        return -1

def short_url(url):
    try:
        host = urlparse(url).netloc.lower().split(':')[0]
        return -1 if host in SHORTENERS else 1
    except:
        return 1

def has_at_symbol(url):
    return -1 if '@' in url else 1

def redirecting_double_slash(url):
    return -1 if url.rfind('//') > 6 else 1

def prefix_suffix_dash(url):
    try:
        domain = tldextract.extract(url).domain or ''
        return -1 if '-' in domain else 1
    except:
        return 1

def count_subdomains(url):
    try:
        ext = tldextract.extract(url)
        sub_count = ext.subdomain.count('.') + (1 if ext.subdomain else 0)
        if sub_count == 0:
            return 1
        elif sub_count == 1:
            return 0
        return -1
    except:
        return 0

def has_https(url):
    scheme = urlparse(url).scheme.lower()
    if scheme == 'https':
        return 1
    elif scheme == 'http':
        return 0
    return -1

def domain_reg_len(url):
    # Không thể xác định WHOIS offline → mặc định an toàn
    return 1

def favicon(url):
    return 1  # Không kiểm favicon thật, giữ giá trị an toàn

def non_std_port(url):
    try:
        parsed = urlparse(url)
        m = PORT_RE.search(parsed.netloc)
        if m:
            port = int(m.group(1))
            return -1 if port not in (80, 443) else 1
        return 1
    except:
        return 1

def https_in_domain(url):
    return -1 if 'https' in urlparse(url).netloc.lower() else 1

def request_url(url):
    return 1

def anchor_url(url):
    return 0

def links_in_script_tags(url):
    return 0

def server_form_handler(url):
    return 1

def info_email(url):
    return -1 if 'mailto:' in url else 1

def abnormal_url(url):
    # Nếu có token nghi ngờ → phishing
    suspicious_tokens = ['login', 'verify', 'update', 'secure', 'confirm', 'account', 'bank', 'password']
    return -1 if any(t in url.lower() for t in suspicious_tokens) else 1

def website_forwarding(url):
    return 0

def status_bar_custom(url):
    return 1

def disable_right_click(url):
    return 1

def using_popup_window(url):
    return 1

def iframe_redirection(url):
    return 1

def age_of_domain(url):
    return 1

def dns_record(url):
    return 1

def website_traffic(url):
    return 0

def pagerank(url):
    return 0

def google_index(url):
    return 1

def links_pointing_to_page(url):
    return 1

def stats_report(url):
    return 1


def extract_features_from_url(url):
    f = {
        'UsingIP': has_ip(url),
        'LongURL': long_url(url),
        'ShortURL': short_url(url),
        'Symbol@': has_at_symbol(url),
        'Redirecting//': redirecting_double_slash(url),
        'PrefixSuffix-': prefix_suffix_dash(url),
        'SubDomains': count_subdomains(url),
        'HTTPS': has_https(url),
        'DomainRegLen': domain_reg_len(url),
        'Favicon': favicon(url),
        'NonStdPort': non_std_port(url),
        'HTTPSDomainURL': https_in_domain(url),
        'RequestURL': request_url(url),
        'AnchorURL': anchor_url(url),
        'LinksInScriptTags': links_in_script_tags(url),
        'ServerFormHandler': server_form_handler(url),
        'InfoEmail': info_email(url),
        'AbnormalURL': abnormal_url(url),
        'WebsiteForwarding': website_forwarding(url),
        'StatusBarCust': status_bar_custom(url),
        'DisableRightClick': disable_right_click(url),
        'UsingPopupWindow': using_popup_window(url),
        'IframeRedirection': iframe_redirection(url),
        'AgeofDomain': age_of_domain(url),
        'DNSRecording': dns_record(url),
        'WebsiteTraffic': website_traffic(url),
        'PageRank': pagerank(url),
        'GoogleIndex': google_index(url),
        'LinksPointingToPage': links_pointing_to_page(url),
        'StatsReport': stats_report(url)
    }
    return f

def features_dict_to_vector(feat_dict, ordered_keys=None):
    default_keys = [
        'UsingIP','LongURL','ShortURL','Symbol@','Redirecting//','PrefixSuffix-','SubDomains',
        'HTTPS','DomainRegLen','Favicon','NonStdPort','HTTPSDomainURL','RequestURL','AnchorURL',
        'LinksInScriptTags','ServerFormHandler','InfoEmail','AbnormalURL','WebsiteForwarding',
        'StatusBarCust','DisableRightClick','UsingPopupWindow','IframeRedirection','AgeofDomain',
        'DNSRecording','WebsiteTraffic','PageRank','GoogleIndex','LinksPointingToPage','StatsReport'
    ]
    if ordered_keys is None:
        ordered_keys = default_keys
    return [feat_dict.get(k, 0) for k in ordered_keys]

def load_dataset(path="data/urls.csv"):
    df = pd.read_csv(path)
    df = df.drop(columns=["Index"], errors="ignore")
    X = df.drop(columns=["class"])
    y = df["class"].replace(-1, 0)
    return X, y
