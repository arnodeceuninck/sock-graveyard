import React from 'react';
import { StyleSheet, View } from 'react-native';
import { WebView } from 'react-native-webview';
import { Platform } from 'react-native';
import { Asset } from 'expo-asset';
import { theme } from '../theme';

export default function PrivacyPolicyScreen() {
  // Load the external HTML file
  const privacyPolicyUri = Platform.select({
    web: require('../../assets/legal/privacy_policy.html'),
    default: Asset.fromModule(require('../../assets/legal/privacy_policy.html')).uri,
  });

  const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Privacy Policy</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
      padding: 1rem;
      color: ${theme.colors.text};
      background-color: ${theme.colors.background};
    }
    h1, h2, h3, h4 {
      line-height: 1.3;
      color: ${theme.colors.primary};
    }
    h2 {
      margin-top: 2rem;
    }
    a {
      color: ${theme.colors.accent};
    }
  </style>
</head>
<body>

<h1>Privacy Policy</h1>
<p>Last updated: January 07, 2026</p>
<p>This Privacy Policy describes Our policies and procedures on the collection, use and disclosure of Your information when You use the Service and tells You about Your privacy rights and how the law protects You.</p>

<p>We use Your Personal data to provide and improve the Service. By using the Service, You agree to the collection and use of information in accordance with this Privacy Policy.</p>

<h2>SUMMARY OF KEY POINTS</h2>

<p><strong><em>This summary provides key points from our Privacy Notice. You can find out more details about any of these topics by using our table of contents below to find the section you are looking for.</em></strong></p>

<p><strong>What personal information do we process?</strong> When you visit, use, or navigate our Services, we may process personal information depending on how you interact with us and the Services, the choices you make, and the products and features you use.</p>

<p><strong>Do we process any sensitive personal information?</strong> We do not process sensitive personal information.</p>

<p><strong>Do we collect any information from third parties?</strong> We do not collect any information from third parties.</p>

<p><strong>How do we process your information?</strong> We process your information to provide, improve, and administer our Services, communicate with you, for security and fraud prevention, and to comply with law. We may also process your information for other purposes with your consent.</p>

<p><strong>In what situations and with which parties do we share personal information?</strong> We may share information in specific situations and with specific third parties.</p>

<p><strong>How do we keep your information safe?</strong> We have adequate organizational and technical processes and procedures in place to protect your personal information. However, no electronic transmission over the internet or information storage technology can be guaranteed to be 100% secure.</p>

<p><strong>What are your rights?</strong> Depending on where you are located geographically, the applicable privacy law may mean you have certain rights regarding your personal information.</p>

<p><strong>How do you exercise your rights?</strong> The easiest way to exercise your rights is by contacting us at <a href="mailto:socks@arnodece.com">socks@arnodece.com</a>. We will consider and act upon any request in accordance with applicable data protection laws.</p>

<h2>1. WHAT INFORMATION DO WE COLLECT?</h2>

<h3>Personal information you disclose to us</h3>

<p><strong><em>In Short:</em></strong> <em>We collect personal information that you provide to us.</em></p>

<p>We collect personal information that you voluntarily provide to us when you register on the Services, express an interest in obtaining information about us or our products and Services, when you participate in activities on the Services, or otherwise when you contact us.</p>

<p><strong>Personal Information Provided by You.</strong> The personal information that we collect depends on the context of your interactions with us and the Services, the choices you make, and the products and features you use. The personal information we collect may include the following:</p>

<ul>
<li>email addresses</li>
<li>passwords</li>
<li>uploaded pictures</li>
</ul>

<p><strong>Sensitive Information.</strong> We do not process sensitive information.</p>

<p><strong>Application Data.</strong> If you use our application(s), we also may collect the following information if you choose to provide us with access or permission:</p>

<ul>
<li><em>Mobile Device Access.</em> We may request access or permission to certain features from your mobile device, including your mobile device's camera, and other features. If you wish to change our access or permissions, you may do so in your device's settings.</li>
</ul>

<p>This information is primarily needed to maintain the security and operation of our application(s), for troubleshooting, and for our internal analytics and reporting purposes.</p>

<p>All personal information that you provide to us must be true, complete, and accurate, and you must notify us of any changes to such personal information.</p>

<h2>2. HOW DO WE PROCESS YOUR INFORMATION?</h2>

<p><strong><em>In Short:</em></strong> <em>We process your information to provide, improve, and administer our Services, communicate with you, for security and fraud prevention, and to comply with law. We may also process your information for other purposes with your consent.</em></p>

<p><strong>We process your personal information for a variety of reasons, depending on how you interact with our Services, including:</strong></p>

<ul>
<li><strong>To facilitate account creation and authentication and otherwise manage user accounts.</strong> We may process your information so you can create and log in to your account, as well as keep your account in working order.</li>
</ul>

<h2>3. WHEN AND WITH WHOM DO WE SHARE YOUR PERSONAL INFORMATION?</h2>

<p><strong><em>In Short:</em></strong> <em>We may share information in specific situations described in this section and/or with the following third parties.</em></p>

<p>We may need to share your personal information in the following situations:</p>

<ul>
<li><strong>Business Transfers.</strong> We may share or transfer your information in connection with, or during negotiations of, any merger, sale of company assets, financing, or acquisition of all or a portion of our business to another company.</li>
</ul>

<h2>4. DO WE OFFER ARTIFICIAL INTELLIGENCE-BASED PRODUCTS?</h2>

<p><strong><em>In Short:</em></strong> <em>We offer products, features, or tools powered by artificial intelligence, machine learning, or similar technologies.</em></p>

<p>As part of our Services, we offer products, features, or tools powered by artificial intelligence, machine learning, or similar technologies (collectively, "AI Products"). These tools are designed to enhance your experience and provide you with innovative solutions.</p>

<p><strong>Our AI Products</strong></p>

<p>Our AI Products are designed for the following functions:</p>

<ul>
<li>AI search (matching uploaded sock images to find potential pairs)</li>
</ul>

<p><strong>How We Process Your Data Using AI</strong></p>

<p>All personal information processed using our AI Products is handled in line with our Privacy Notice and our agreement with third parties. This ensures high security and safeguards your personal information throughout the process, giving you peace of mind about your data's safety.</p>

<h2>5. HOW LONG DO WE KEEP YOUR INFORMATION?</h2>

<p><strong><em>In Short:</em></strong> <em>We keep your information for as long as necessary to fulfill the purposes outlined in this Privacy Notice unless otherwise required by law.</em></p>

<p>We will only keep your personal information for as long as it is necessary for the purposes set out in this Privacy Notice, unless a longer retention period is required or permitted by law (such as tax, accounting, or other legal requirements). No purpose in this notice will require us keeping your personal information for longer than the period of time in which users have an account with us.</p>

<p>When we have no ongoing legitimate business need to process your personal information, we will either delete or anonymize such information, or, if this is not possible (for example, because your personal information has been stored in backup archives), then we will securely store your personal information and isolate it from any further processing until deletion is possible.</p>

<h2>6. HOW DO WE KEEP YOUR INFORMATION SAFE?</h2>

<p><strong><em>In Short:</em></strong> <em>We aim to protect your personal information through a system of organizational and technical security measures.</em></p>

<p>We have implemented appropriate and reasonable technical and organizational security measures designed to protect the security of any personal information we process. However, despite our safeguards and efforts to secure your information, no electronic transmission over the Internet or information storage technology can be guaranteed to be 100% secure, so we cannot promise or guarantee that hackers, cybercriminals, or other unauthorized third parties will not be able to defeat our security and improperly collect, access, steal, or modify your information. Although we will do our best to protect your personal information, transmission of personal information to and from our Services is at your own risk. You should only access the Services within a secure environment.</p>

<h2>7. DO WE COLLECT INFORMATION FROM MINORS?</h2>

<p><strong><em>In Short:</em></strong> <em>We do not knowingly collect data from or market to children under 18 years of age.</em></p>

<p>We do not knowingly collect, solicit data from, or market to children under 18 years of age, nor do we knowingly sell such personal information. By using the Services, you represent that you are at least 18 or that you are the parent or guardian of such a minor and consent to such minor dependent's use of the Services. If we learn that personal information from users less than 18 years of age has been collected, we will deactivate the account and take reasonable measures to promptly delete such data from our records. If you become aware of any data we may have collected from children under age 18, please contact us at <a href="mailto:socks@arnodece.com">socks@arnodece.com</a>.</p>

<h2>8. WHAT ARE YOUR PRIVACY RIGHTS?</h2>

<p><strong><em>In Short:</em></strong> <em>Depending on your state of residence in the US or in some regions, such as the European Economic Area (EEA), United Kingdom (UK), Switzerland, and Canada, you have rights that allow you greater access to and control over your personal information. You may review, change, or terminate your account at any time.</em></p>

<p>In some regions (like the EEA, UK, Switzerland, and Canada), you have certain rights under applicable data protection laws. These may include the right (i) to request access and obtain a copy of your personal information, (ii) to request rectification or erasure; (iii) to restrict the processing of your personal information; (iv) if applicable, to data portability; and (v) not to be subject to automated decision-making. In certain circumstances, you may also have the right to object to the processing of your personal information.</p>

<p>We will consider and act upon any request in accordance with applicable data protection laws.</p>

<p><strong><u>Withdrawing your consent:</u></strong> If we are relying on your consent to process your personal information, you have the right to withdraw your consent at any time. You can withdraw your consent at any time by contacting us using the contact details provided below.</p>

<h3>Account Information</h3>

<p>If you would at any time like to review or change the information in your account or terminate your account, you can contact us using the contact information provided.</p>

<p>Upon your request to terminate your account, we will deactivate or delete your account and information from our active databases. However, we may retain some information in our files to prevent fraud, troubleshoot problems, assist with any investigations, enforce our legal terms and/or comply with applicable legal requirements.</p>

<p>If you have questions or comments about your privacy rights, you may email us at <a href="mailto:socks@arnodece.com">socks@arnodece.com</a>.</p>

<h2>9. CONTROLS FOR DO-NOT-TRACK FEATURES</h2>

<p>Most web browsers and some mobile operating systems and mobile applications include a Do-Not-Track ("DNT") feature or setting you can activate to signal your privacy preference not to have data about your online browsing activities monitored and collected. At this stage, no uniform technology standard for recognizing and implementing DNT signals has been finalized. As such, we do not currently respond to DNT browser signals or any other mechanism that automatically communicates your choice not to be tracked online. If a standard for online tracking is adopted that we must follow in the future, we will inform you about that practice in a revised version of this Privacy Notice.</p>

<h2>10. DO UNITED STATES RESIDENTS HAVE SPECIFIC PRIVACY RIGHTS?</h2>

<p><strong><em>In Short:</em></strong> <em>If you are a resident of California, Colorado, Connecticut, Delaware, Florida, Indiana, Iowa, Kentucky, Maryland, Minnesota, Montana, Nebraska, New Hampshire, New Jersey, Oregon, Rhode Island, Tennessee, Texas, Utah, or Virginia, you may have the right to request access to and receive details about the personal information we maintain about you and how we have processed it, correct inaccuracies, get a copy of, or delete your personal information. You may also have the right to withdraw your consent to our processing of your personal information. These rights may be limited in some circumstances by applicable law.</em></p>

<p>For more details about US state privacy rights, please contact us at <a href="mailto:socks@arnodece.com">socks@arnodece.com</a>.</p>

<h2>11. DO WE MAKE UPDATES TO THIS NOTICE?</h2>

<p><strong><em>In Short:</em></strong> <em>Yes, we will update this notice as necessary to stay compliant with relevant laws.</em></p>

<p>We may update this Privacy Notice from time to time. The updated version will be indicated by an updated "Revised" date at the top of this Privacy Notice. If we make material changes to this Privacy Notice, we may notify you either by prominently posting a notice of such changes or by directly sending you a notification. We encourage you to review this Privacy Notice frequently to be informed of how we are protecting your information.</p>

<h2>12. HOW CAN YOU CONTACT US ABOUT THIS NOTICE?</h2>

<p>If you have questions or comments about this notice, you may email us at <a href="mailto:socks@arnodece.com">socks@arnodece.com</a> or contact us by post at:</p>

<p>
<strong>Arno Deceuninck</strong><br/>
Belgium
</p>

<h2>13. HOW CAN YOU REVIEW, UPDATE, OR DELETE THE DATA WE COLLECT FROM YOU?</h2>

<p>You have the right to request access to the personal information we collect from you, details about how we have processed it, correct inaccuracies, or delete your personal information. You may also have the right to withdraw your consent to our processing of your personal information. These rights may be limited in some circumstances by applicable law. To request to review, update, or delete your personal information, please visit: <a href="mailto:socks@arnodece.com">socks@arnodece.com</a>.</p>

</body>
</html>
  `;

  return (
    <View style={styles.container}>
      <WebView
        originWhitelist={['*']}
        source={{ html: htmlContent }}
        style={styles.webview}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  webview: {
    flex: 1,
  },
});
